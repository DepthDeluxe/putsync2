import logging

from flask import Flask, request, jsonify

import putioscanner

logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/robots.txt')
def robots():
    return '''User-Agent: *
Disallow: *'''


@app.route('/trigger', methods=['POST'])
def trigger():
    logger.info('POST data: %s', request.form)
    putioscanner.scan(int(request.form.get('file_id', 0)))

    response = {
        'route': '/trigger',
        'folder': {
            'id': request.form.get('file_id', None),
        }
    }
    return jsonify(response), 200


@app.route('/full', methods=['POST'])
def full():
    logger.info(f'POST data: {request.form}')
    putioscanner.scan()

    response = {
        'route': '/full',
        'folder': {
            'id': 0,
        }
    }
    return jsonify(response), 200
