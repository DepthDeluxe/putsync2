import logging
import re

from flask import Flask, request, jsonify, send_from_directory, abort

from .api import api
from .core.configuration import getserverconfig

logger = logging.getLogger(__name__)
app = Flask(__name__, static_url_path='')

# app.config.update(
#     DEBUG=True,
# )

def validatewhitelist():
    logger.info(f'Incoming address {request.remote_addr}')
    incoming_quartet = request.remote_addr.split('.')
    if not re.match('192\.168\.|127\.0\.0\.1', request.remote_addr):
        abort(403)


@app.route('/')
def index():
    validatewhitelist()
    return send_from_directory(getserverconfig().dist_path, 'index.html')


@app.route('/robots.txt')
def robots():
    return '''User-Agent: *
Disallow: *'''


@app.route('/assets/<path:path>')
def assets(path):
    validatewhitelist()
    return send_from_directory(getserverconfig().dist_path, path)

app.register_blueprint(api)
