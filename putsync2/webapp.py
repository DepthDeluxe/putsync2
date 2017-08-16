import logging

from flask import Flask, request, jsonify, send_from_directory

from .api import api
from .core.configuration import getserverconfig

logger = logging.getLogger(__name__)
app = Flask(__name__, static_url_path='')

# app.config.update(
#     DEBUG=True,
# )


@app.route('/')
def index():
    logger.error('XXXXXXX')
    return send_from_directory('../build/dist', 'index.html')


@app.route('/robots.txt')
def robots():
    return '''User-Agent: *
Disallow: *'''


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory(getserverconfig().dist_path, path)

app.register_blueprint(api)
