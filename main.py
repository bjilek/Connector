import time
import multiprocessing
import traceback
import logging
import os
import sys
import argparse
import webbrowser
from logging import handlers
from waitress import serve

from connector.server import app
from connector import resources

VERSION = '0.3.0'

_logger = logging.getLogger(__name__)


class Process(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = multiprocessing.Pipe()
        self._exception = None

    def run(self):
        try:
            multiprocessing.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--open-browser',
        help='Opens a browser window to show the application',
        action='store_true'
    )
    args = parser.parse_args()
    return args


def run_app():
    app.config.update(resources.get_config())
    _logger.info(
        'Starting Connector with allowed origins: '
        f'{app.config["ALLOWED_ORIGINS"]}'
    )

    serve(app, host='localhost', port=app.config['CONNECTOR_PORT'])


def setup_logger():
    filename = resources.get_log_path()
    log_handler = logging.handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=1000000,
        backupCount=5
    )

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-8s] %(message)s',
        handlers=[log_handler]
    )


def terminate_server(server):
    _logger.info('Terminating Server')
    server.terminate()
    server.join()


def update():
    _logger.info('Updating connector')

    try:
        resources.download_update()
        resources.switch_binary()
        _logger.info('Connector update completed')
    except Exception as e:
        _logger.error('Error while updating')
        _logger.error(e)
    finally:
        resources.delete_user_data('update')


def restart_program():
    _logger.info('Restarting connector')
    os.spawnl(os.P_NOWAIT, sys.executable, *sys.argv)
    sys.exit(0)


def cleanup():
    resources.delete_user_data('update')
    resources.delete_old_binary()
    resources.delete_user_data('restart')


def main():
    multiprocessing.freeze_support()
    resources.set_config({
        'ALLOWED_ORIGINS': ['*'],
        'CONNECTOR_PORT': 5050,
        'UPDATE_URL':
            'https://github.com/bjilek/Connector/'
            'releases/download/latest/connector'
    })
    cleanup()
    args = parse_args()
    server = Process(name='connector', target=run_app)
    server.start()
    time.sleep(1)

    if server.exception:
        error, trace_back = server.exception
        _logger.error(trace_back)

    if args.open_browser:
        port = resources.get_config()['CONNECTOR_PORT']
        webbrowser.open(f'http://localhost:{port}', new=1)

    while not time.sleep(5):
        if resources.is_binary() and resources.update_file_exists():
            update()
            terminate_server(server)
            restart_program()
            break
        if resources.user_data_exists('restart'):
            resources.delete_user_data('restart')
            terminate_server(server)
            restart_program()
            break


setup_logger()

if __name__ == '__main__':
    main()
