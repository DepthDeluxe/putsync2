import logging

from flask import Flask, request, jsonify, send_from_directory

from .api import api

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
def xxx(path):
    return send_from_directory('../build/dist', path)

app.register_blueprint(api)
