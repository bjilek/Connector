import sys
import os
import stat
import json
import requests
import logging
from pathlib import Path

_logger = logging.getLogger()


def is_binary():
    return hasattr(sys, '_MEIPASS')


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def binary_file_name():
    return sys.executable


def binary_update_file_name():
    return binary_file_name() + '.update'


def update_url():
    file_extension = '_win.exe' if sys.platform == 'win32' else '_linux'
    return get_config()['UPDATE_URL'] + file_extension


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


def set_config(config_values):
    config_path = get_config_path()

    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            config_values.update(json.load(f))

    with open(config_path, 'w') as f:
        json.dump(config_values, f, indent=4)


def get_config():
    config_path = get_config_path()

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def create_update_file():
    update_file = get_user_data('update')

    if not os.path.isfile(update_file):
        with open(update_file, 'w') as f:
            f.write('Update queued')


def read_update_file():
    update_file = get_user_data('update')

    if update_file.is_file():
        with open(update_file, 'r') as f:
            return f.read()

    return ''


def write_update_file(line):
    update_file = get_user_data('update')

    if update_file.is_file():
        with open(update_file, 'w') as f:
            f.write(line)


def update_file_exists():
    update_file = get_user_data('update')
    return os.path.isfile(update_file)


def create_user_data(filename):
    file_path = get_user_data(filename)

    if not os.path.isfile(file_path):
        open(file_path, 'w').close()

    return file_path


def delete_user_data(filename):
    file_path = get_user_data(filename)

    if os.path.isfile(file_path):
        os.remove(file_path)


def user_data_exists(filename):
    return os.path.isfile(get_user_data(filename))


def download_update():
    filename = binary_update_file_name()

    with requests.get(update_url(), stream=True) as r:
        r.raise_for_status()
        with open(resource_path(filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return resource_path(filename)


def delete_old_binary():
    filename = binary_file_name() + '.old'
    if os.path.isfile(filename):
        os.remove(filename)


def switch_binary():
    old_binary = binary_file_name()
    new_binary = binary_update_file_name()
    if os.path.isfile(old_binary) and os.path.isfile(new_binary):
        os.rename(old_binary, old_binary + '.old')
        os.rename(new_binary, old_binary)
        os.chmod(old_binary, stat.S_IRWXU)
