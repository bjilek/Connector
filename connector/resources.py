import sys
import os
import stat
import json
import requests
from pathlib import Path


def is_binary():
    return hasattr(sys, '_MEIPASS')


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def binary_file_name():
    return sys.executable


def binary_update_file_name():
    return binary_file_name() + '.update'


def update_url():
    return get_config()['UPDATE_URL']


def get_user_data_path():
    if sys.platform == 'linux':
        path = Path(f'~/.local/share/connector/').expanduser()
        path.mkdir(parents=True, exist_ok=True)
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
                'CONNECTOR_PORT': 5050,
                'UPDATE_URL':
                    'https://github.com/bjilek/Connector/'
                    'releases/download/latest/connector'
            }, f, indent=4)


def get_config():
    config_path = get_config_path()

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def create_update_file():
    update_file = get_user_data('update')

    if not os.path.isfile(update_file):
        open(update_file, 'a').close()


def delete_update_file():
    update_file = get_user_data('update')

    if os.path.isfile(update_file):
        os.remove(update_file)


def update_file_exists():
    update_file = get_user_data('update')
    return os.path.isfile(update_file)


def download_update():
    filename = binary_update_file_name()

    with requests.get(update_url(), stream=True) as r:
        r.raise_for_status()
        with open(resource_path(filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return resource_path(filename)


def switch_binary():
    old_binary = binary_file_name()
    new_binary = binary_update_file_name()
    if os.path.isfile(old_binary) and os.path.isfile(new_binary):
        os.rename(old_binary, old_binary + '.old')
        os.rename(new_binary, old_binary)
        os.remove(old_binary + '.old')
        os.chmod(old_binary, stat.S_IRWXU)
