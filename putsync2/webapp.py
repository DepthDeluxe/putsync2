import logging

from flask import Flask, request, jsonify

from .api import api

logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/robots.txt')
def robots():
    return '''User-Agent: *
Disallow: *'''

app.register_blueprint(api)
