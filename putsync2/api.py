import logging
import flask
import sys

from pony.orm import db_session, select, count, sum, desc, max
import putiopy

from .core import filecollection
from .core.models.file import File
from .core.models.syncattempt import SyncAttempt
from .core.scanner import Scanner
from .core.configuration import PutsyncConfig

api = flask.Blueprint(__name__, __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api.route('/trigger', methods=['POST'])
def trigger():
    logger.info('POST data: %s', flask.request.form)
    Scanner().scan(int(flask.request.form.get('file_id', 0)))

    response = {
        'route': '/trigger',
        'folder': {
            'id': flask.request.form.get('file_id', None),
        }
    }
    return flask.jsonify(response), 200


@api.route('/full', methods=['POST'])
def full():
    logger.info(f'POST data: {flask.request.form}')
    Scanner().scan()

    response = {
        'route': '/full',
        'folder': {
            'id': 0,
        }
    }
    return flask.jsonify(response), 200


@api.route('/downloads')
@db_session
def downloads():
    status = flask.request.args.get('status', 'done')
    page = flask.request.args.get('page', 0, type=int)
    page_size = flask.request.args.get('page-size', 25, type=int)

    files, file_count = filecollection.synchistory(status, page+1, page_size)
    out = {
        'count': file_count,
        'data': [f.to_dict() for f in files]
    }

    return flask.json.dumps(out)


@api.route('/downloads/retry/<int:id>', methods=['POST'])
@db_session
def retrydownload(id):
    file = File[id].markforretry()

    return flask.jsonify({
        'data': file.to_dict()
    })


@api.route('/add', methods=['POST'])
def add():
    magnet_link = flask.request.json['magnet_link']

    client = putiopy.Client(PutsyncConfig().putio_token)
    client.Transfer.add_url(magnet_link)

    return 'Accepted', 202


@api.route('/statistics')
def statistics():
    total_bytes = filecollection.bytesndays(100000)
    last_day_bytes = filecollection.bytesndays(1)
    last_month_bytes = filecollection.bytesndays(30)

    total_count = filecollection.countndays(100000)
    last_day_count = filecollection.countndays(1)
    last_month_count = filecollection.countndays(30)

    # get last download time
    last_download_time = None

    return flask.jsonify({
        'data': {
            'bytes': {
                'total': total_bytes,
                '1day': last_day_bytes,
                '30days': last_month_bytes
            },
            'count': {
                'total': total_count,
                '1day': last_day_count,
                '30days': last_month_count
            },
            'last_time': last_download_time,
            }
        })
