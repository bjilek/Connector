import logging
import json

from flask import Flask, request, Response, jsonify, render_template, redirect

from . import printer
from . import resources

_logger = logging.getLogger()

app = Flask(__name__)


@app.before_request
def before_request():
    origin = request.origin

    if origin:
        allowed_origins = get_allowed_origins()

        if '*' not in allowed_origins and origin not in allowed_origins:
            return Response(status=403)


@app.after_request
def after_request(response):
    origin = request.origin

    if origin:
        allowed_origins = get_allowed_origins()

        if '*' in allowed_origins or origin in allowed_origins:
            if '*' in allowed_origins:
                origin = '*'

            header = response.headers
            header['Access-Control-Allow-Origin'] = origin
            header['Access-Control-Allow-Headers'] = 'Content-Type'

    return response


def get_allowed_origins():
    return app.config.get('ALLOWED_ORIGINS', [])


def clean_printer_name(name: str):
    return name.replace('+', ' ')


def url_safe_name(name: str):
    return name.strip().replace(' ', '+') if isinstance(name, str) else name


def get_context(display_id=None):
    file = f'display_{display_id}.json' \
        if display_id is not None else 'display.json'

    try:
        ctx = json.load(open(resources.get_user_data(file)))
    except FileNotFoundError:
        ctx = {}
    except Exception as e:
        _logger.warning(e)
        raise e

    return ctx


def _set_display(display_id=None):
    filename = f'display_{display_id}.json' if display_id else 'display.json'
    file = resources.get_user_data(filename)

    error = None
    status = 200

    try:
        with open(file, 'w') as context:
            json.dump(request.data, context, indent=4)
    except json.JSONDecodeError as e:
        _logger.error(e)
        error = e
        status = 400
    except Exception as e:
        _logger.error(e)
        error = e
        status = 500

    return error, status


@app.route("/")
def available_printer():
    printer_list = printer.list_printer()

    return render_template(
        'printer_list.html', **{'printer_list': printer_list}
    )


@app.route('/testprint/<string:printer_name>', methods=['GET'])
def print_testpage(printer_name):
    printer_name = clean_printer_name(printer_name)
    _logger.info(f'Sending test print job to {printer_name}')
    try:
        printer.test_print(printer_name)
    except Exception as e:
        _logger.error(e)

    return redirect('/')


@app.route('/api/v1/print', methods=['POST'])
def print_to_default():
    printer_name = printer.get_default_printer()

    if printer_name is None:
        return jsonify({'error': 'No default printer set'}, status=500)

    return Response(status=200)


@app.route("/api/v1/print/<string:printer_name>", methods=['POST'])
def print_file(printer_name):
    printer_name = clean_printer_name(printer_name)
    _logger.info(f'Sending print job to {printer_name}')

    try:
        printer.print_to(printer_name, request.data)
    except Exception as e:
        _logger.error(e)
        return jsonify({'error': e}, status=500)

    return Response(status=200)


@app.route('/api/v1/list_printer', methods=['GET'])
def get_printer_names():
    return jsonify({
        'printer': [url_safe_name(p) for p in printer.list_printer()],
        'default': url_safe_name(printer.get_default_printer())
    })


@app.route('/api/v1/default_printer', methods=['GET'])
def get_default_printer_name():
    return jsonify({
        'default_printer': url_safe_name(
            printer.get_default_printer()
        )})


@app.route('/api/v1/set_display', methods=['POST'])
def set_display():
    error, status = _set_display()

    if error:
        return jsonify({'error': error}, status=status)

    return Response(status=status)


@app.route('/api/v1/set_display/<string:display_id>', methods=['POST'])
def set_extra_display(display_id):
    error, status = _set_display(display_id)

    if error:
        return jsonify({'error': error}, status=status)

    return Response(status=status)


@app.route('/display', methods=['GET'])
def display():
    try:
        ctx = get_context()
    except Exception as e:
        return jsonify({'error': e}, status=404)

    return render_template('display.html', **ctx)


@app.route('/display/<string:display_id>', methods=['GET'])
def extra_display(display_id):
    try:
        ctx = get_context(display_id)
    except Exception as e:
        return jsonify({'error': e}, status=404)

    return render_template('display.html', **ctx)


@app.route('/update', methods=['GET'])
def update():
    try:
        resources.create_update_file()
    except Exception as e:
        return jsonify({'error': e}, status=500)

    return Response(status=200)
