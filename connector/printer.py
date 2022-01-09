import os
import sys
import subprocess
import logging
import re
from uuid import uuid4
from shutil import which

if sys.platform == 'win32':
    import win32print
    import win32api

from .resources import get_user_data, get_user_data_path, resource_path

_logger = logging.getLogger(__name__)


def clean_printer_name(name):
    return re.sub(r'[\>\<\|\&]', '', name)


def list_printer():
    printer_list = []
    if sys.platform in ['linux', 'darwin']:
        try:
            printer = subprocess.check_output(['lpstat', '-p']).decode()
            printer_list.extend([p for p in printer.splitlines()])
            printer_list = [p.split(' ')[1] for p in printer_list]
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
                default_printer = default_printer.split(' ')[2]
            else:
                default_printer = None
        except subprocess.CalledProcessError as e:
            _logger.error(e)
        except IndexError as e:
            _logger.error(e)
    elif sys.platform == 'win32':
        default_printer = win32print.GetDefaultPrinter()

    return default_printer


def print_to(printername, file):
    name = clean_printer_name(printername)

    filepath = get_user_data(
        f'tmp_{str(uuid4())[:8]}.pdf'
    ).absolute()

    try:
        with open(filepath, 'wb') as f:
            f.write(file)

            if sys.platform in ['linux', 'darwin']:
                print_unix(name, filepath)
            elif sys.platform == 'win32':
                print_win(name, filepath)
            else:
                raise NotImplementedError('Platform not supported')
    except Exception as e:
        _logger.error(e)
    finally:
        os.remove(filepath)


def print_unix(printername, filepath):
    args = ['lpr', '-P', f'{printername}', filepath]
    subprocess.check_output(args)


def print_win(printername, filepath):
    if which('gswin64c.exe') is not None:
        print_win_gs('gswin64c.exe', printername, filepath)
    elif which('gswin32c.exe') is not None:
        print_win_gs('gswin32c.exe', printername, filepath)
    else:
        print_win_shell(printername, filepath)


def print_win_gs(exe, printername, filepath):
    args = [
        exe, '-sDEVICE=mswinpr2', '-dBATCH', '-dNOPAUSE',
        '-dFitPage', f'-sOutputFile="%printer%{printername}"', filepath
    ]

    subprocess.check_output(args)


def print_win_shell(printername, filepath):
    filename = str(filepath).split('\\')[-1]

    win32api.ShellExecute(
        0, 'print', filename, f'/d:{printername}', get_user_data_path(), 0
    )


def test_print(printer_name):
    with open(str(resource_path('testpage.pdf')), 'rb') as file:
        print_to(printer_name, file.read())
