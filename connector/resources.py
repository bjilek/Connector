import sys
import os
import json
from pathlib import Path


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_user_data_path():
    if sys.platform == 'linux':
        path = Path(f'~/.local/share/connector/').expanduser()
    elif sys.platform == 'win32':
        path = os.path.expandvars('%LOCALAPPDATA%\\Connector\\')
        Path(path).mkdir(parents=True, exist_ok=True)
    else:
        path = Path('.')

    return path


def get_user_data(filename):
    return Path(get_user_data_path(), filename)


def get_config_path():
    return get_user_data('config.json')


def get_log_path():
    return get_user_data('connector.log')


def set_config():
    config_path = get_config_path()

    if not os.path.isfile(config_path):
        with open(config_path, 'w') as f:
            json.dump({
                'ALLOWED_ORIGINS': ['*'],
                'CONNECTOR_PORT': 5050
            }, f, indent=4)


def get_config():
    config_path = get_config_path()

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config
