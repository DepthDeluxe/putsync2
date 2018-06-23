import logging
from flask import Blueprint, request, jsonify, json
from flask import current_app as app

from ..db import serialize_obj, SessionContext
from ..core.file import FileStatus, FileCollection
from ..core.scanner import Scanner
from ..core.putio import create_client
from ..core.task import Task

api = Blueprint(__name__, __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


def get_config():
    return app.config['PUTSYNC_CONFIGURATION_MANAGER'].get().backend


@api.route('/trigger', methods=['POST'])
def trigger():
    logger.info('POST data: %s', request.form)
    file_id = int(request.form.get('file_id', 0))
    putio_token = get_config().putio_token

    with Scanner(putio_token, f'triggered-{file_id}') as scanner:
        scanner.scan(file_id)

    response = {
        'route': '/trigger',
        'folder': {
            'id': request.form.get('file_id', None),
        }
    }
    return jsonify(response), 200


@api.route('/full', methods=['POST'])
def full():
    logger.info(f'POST data: {request.form}')

    with Scanner('triggered-full') as scanner:
        scanner.scan()

    response = {
        'route': '/full',
        'folder': {
            'id': 0,
        }
    }
    return jsonify(response), 200


@api.route('/downloads')
def downloads():
    status = FileStatus(request.args.get('status', 'done', type=str))
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page-size', 25, type=int)

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

        return json.dumps(out)


@api.route('/add', methods=['POST'])
def add():
    magnet_link = request.json['magnet_link']

    client = create_client(get_config().putio_token)
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

    return jsonify({
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


@api.route('/tasks')
def tasks():
    return jsonify([
        t.to_dict()
        for t in Task.instances()
    ])
