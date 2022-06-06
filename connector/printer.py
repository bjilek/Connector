import os
import sys
import subprocess
import logging
import time
from uuid import uuid4
from shutil import which

if sys.platform == 'win32':
    import win32print
    import win32api

from .resources import (
    get_user_data, get_user_data_path, resource_path, get_config
)

_logger = logging.getLogger(__name__)


def list_printer():
    printer_list = []
    if sys.platform in ['linux', 'darwin']:
        try:
            printer = subprocess.check_output(['lpstat', '-a']).decode()
            printer_list.extend([p for p in printer.splitlines()])
            printer_list = [p.split(' ')[0] for p in printer_list]
        except subprocess.CalledProcessError as e:
            _logger.error(e)
    elif sys.platform == 'win32':
        printer = win32print.EnumPrinters(6)
        printer_list.extend([p[2] for p in printer])

    return printer_list


def get_default_printer():
    default_printer = None
    if sys.platform in ['linux', 'darwin']:
        try:
            default_printer = subprocess.check_output(
                ['lpstat', '-d']).decode().strip()
            if ':' in default_printer:
                default_printer = default_printer.split(' ')[-1]
            else:
                default_printer = None
        except subprocess.CalledProcessError as e:
            _logger.error(e)
        except IndexError as e:
            _logger.error(e)
    elif sys.platform == 'win32':
        default_printer = win32print.GetDefaultPrinter()

    return default_printer


def print_to(printer_name, file):
    filepath = get_user_data(
        f'tmp_{str(uuid4())[:8]}.pdf'
    ).absolute()

    try:
        with open(filepath, 'wb') as f:
            f.write(file)

        if sys.platform in ['linux', 'darwin']:
            print_unix(printer_name, filepath)
        elif sys.platform == 'win32':
            print_win(printer_name, filepath)
        else:
            raise NotImplementedError('Platform not supported')
    except Exception as e:
        _logger.error(e)
    finally:
        if os.path.isfile(filepath):
            os.remove(filepath)


def print_unix(printer_name, filepath):
    _logger.info(f'Printing with provider lpr')
    args = ['lpr', '-o', 'noPdfAutoRotate', '-P', f'{printer_name}', str(filepath)]
    subprocess.check_output(args)


def print_win(printername, filepath):
    config = get_config()

    if config.get('GS_PATH'):
        print_win_gs(config.get('GS_PATH'), printername, filepath)
    else:
        if which('gswin64c.exe') is not None:
            print_win_gs('gswin64c.exe', printername, filepath)
        elif which('gswin32c.exe') is not None:
            print_win_gs('gswin32c.exe', printername, filepath)
        elif os.path.isfile(resource_path('gswin64c.exe')):
            print_win_gs(resource_path('gswin64c.exe'), printername, filepath)
        else:
            print_win_shell(printername, filepath)


def print_win_gs(exe, printername, filepath):
    _logger.info(f'Printing with provider {exe}')
    args = [
        exe, '-sDEVICE=mswinpr2', '-dBATCH', '-dNOPAUSE',
        '-dFitPage', f'-sOutputFile="%printer%{printername}"', filepath
    ]

    subprocess.check_output(args)


def print_win_shell(printername, filepath):
    _logger.info(f'Printing with provider ShellExecute')
    filename = str(filepath).split('\\')[-1]

    win32api.ShellExecute(
        0, 'print', filename, f'/d:{printername}', get_user_data_path(), 0
    )

    time.sleep(get_config().get('SHELLEXECUTE_TIMEOUT', 1))


def test_print(page_format, printer_name):
    file_name = f'testpage_{page_format}.pdf'
    with open(resource_path(file_name), 'rb') as file:
        print_to(printer_name, file.read())
