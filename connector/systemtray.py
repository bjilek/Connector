import webbrowser

from PIL import Image
from pystray import Menu, MenuItem, Icon

from .resources import resource_path, get_config


def build_icon():
    if Icon.HAS_MENU:
        menu = Menu(
            MenuItem('Open', show, default=True),
            MenuItem('Quit', stop)
        )
    else:
        menu = Menu(MenuItem('Open', show, default=True))

    image_path = resource_path('connector/static/icons/connector48x48.png')

    tray_icon = Icon(
        'Connector', icon=Image.open(image_path),
        title='Connector', menu=menu
    )

    return tray_icon


def show():
    port = get_config()['CONNECTOR_PORT']
    webbrowser.open(f'http://localhost:{port}', new=1)


def stop(icon):
    icon.stop()
