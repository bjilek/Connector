import time
import multiprocessing
import traceback
import logging
import os
import sys
from logging import handlers
from waitress import serve

from connector.server import app
from connector import resources

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
    except Exception as e:
        _logger.error(e)
    finally:
        resources.delete_update_file()

    _logger.info('Connector update completed')

    return True


def restart_program():
    _logger.info('Restarting connector')
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    sys.exit(0)


def cleanup():
    resources.delete_update_file()
    resources.delete_old_binary()


def main():
    cleanup()
    server = Process(name='connector', target=run_app)
    server.start()
    time.sleep(1)

    if server.exception:
        error, traceback = server.exception
        _logger.error(traceback)

    while not time.sleep(5):
        if resources.is_binary() and resources.update_file_exists():
            update()
            terminate_server(server)
            restart_program()

    terminate_server(server)
    _logger.info('Connector terminated')

setup_logger()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    resources.set_config()
    main()
