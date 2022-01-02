import os
import sys
import subprocess
import logging
import re

if sys.platform == 'win32':
    import win32print

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


def print_to(name, file):
    name = clean_printer_name(name)
    with open('tmp_file.pdf', 'wb') as f:
        f.write(file)

        if sys.platform in ['linux', 'darwin']:
            args = ['lpr', '-P', f'{name}', 'tmp_file.pdf']
        elif sys.platform == 'win32':
            args = [
                'gswin64c.exe', '-sDEVICE=mswinpr2', '-dBATCH', '-dNOPAUSE',
                '-dFitPage', f'-sOutputFile="%printer%{name}"', 'tmp_file.pdf'
            ]
        else:
            raise NotImplementedError('Platform not supported')

        try:
            subprocess.check_output(args)
        except subprocess.CalledProcessError as e:
            _logger.error(e)
        except Exception as e:
            _logger.error(e)
            raise e

    os.remove('tmp_file.pdf')
