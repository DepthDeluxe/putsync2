import logging

from flask import Flask, send_from_directory

from .api import api
from .core.configuration import getserverconfig

logger = logging.getLogger(__name__)
app = Flask(__name__, static_url_path='')


@app.route('/')
def index():
    return send_from_directory(getserverconfig().dist_path, 'index.html')


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory(getserverconfig().dist_path, path)


app.register_blueprint(api)
