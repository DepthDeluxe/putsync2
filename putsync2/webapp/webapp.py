import logging
import os

from flask import Flask, send_from_directory

from .api import api

logger = logging.getLogger(__name__)
app = Flask('putsync', static_url_path='')


def get_config():
    return app.config['PUTSYNC_CONFIGURATION_MANAGER'].get().webapp


@app.route('/')
def index():
    return send_from_directory(get_config().dist_path, 'index.html')


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory(os.path.abspath(get_config().dist_path), path)


app.register_blueprint(api)
