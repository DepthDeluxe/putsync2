import logging

from flask import Flask, send_from_directory

from .api import api
from .core.configuration import config_instance

logger = logging.getLogger('application')
app = Flask('application', static_url_path='')


@app.route('/')
def index():
    return send_from_directory(config_instance().dist_path, 'index.html')


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory(config_instance().absolutedistpath(), path)


app.register_blueprint(api)


if __name__ == '__main__':
    app.run(port=9000)
