import time
import multiprocessing
import traceback
import logging
from logging import handlers
from waitress import serve

from connector.server import app
from connector.resources import set_config, get_config, get_log_path
from connector.systemtray import build_icon

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
    app.config.update(get_config())
    _logger.info(
        'Starting Connector with allowed origins: '
        f'{app.config["ALLOWED_ORIGINS"]}'
    )

    serve(app, host='localhost', port=app.config['CONNECTOR_PORT'])


def setup_logger():
    filename = get_log_path()
    log_handler = logging.handlers.WatchedFileHandler(
        filename=filename,
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


def run_icon():
    icon = build_icon()
    icon.run()


def main():
    server = Process(name='connector', target=run_app)
    server.start()
    time.sleep(1)

    if server.exception:
        error, traceback = server.exception
        _logger.error(traceback)
    else:
        run_icon()

    terminate_server(server)
    _logger.info('Closing Connector')


setup_logger()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    set_config()
    main()
