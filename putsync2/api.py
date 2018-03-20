import logging
import flask

import putiopy

from .core.db import serialize_obj
from .core.db import SessionContext
from .core.models.file import File, FileStatus, FileCollection
from .core.scanner import Scanner
from .core.configuration import config_instance

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
def downloads():
    status = FileStatus(flask.request.args.get('status', 'done', type=str))
    page = flask.request.args.get('page', 1, type=int)
    page_size = flask.request.args.get('page-size', 25, type=int)

    with SessionContext() as session:
        files, file_count = FileCollection(session).query(
            status,
            page-1,
            page_size
        )

        out = {
            'count': file_count,
            'data': [serialize_obj(f) for f in files]
        }

        return flask.json.dumps(out)


@api.route('/downloads/retry/<int:id>', methods=['POST'])
def retrydownload(id):
    file = File[id].markforretry()

    return flask.jsonify({
        'data': serialize_obj(file)
    })


@api.route('/add', methods=['POST'])
def add():
    magnet_link = flask.request.json['magnet_link']

    client = putiopy.Client(config_instance().putio_token)
    client.Transfer.add_url(magnet_link)

    return 'Accepted', 202


@api.route('/statistics')
def statistics():
    with SessionContext() as session:
        file_collection = FileCollection(session)

        total_bytes = file_collection.bytesndays(100000)
        last_day_bytes = file_collection.bytesndays(1)
        last_month_bytes = file_collection.bytesndays(30)

        total_count = file_collection.countndays(100000)
        last_day_count = file_collection.countndays(1)
        last_month_count = file_collection.countndays(30)

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
