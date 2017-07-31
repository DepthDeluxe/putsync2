import logging
import flask

from pony import orm

from .core import putioscanner
from .core.models.download import Download, DownloadStatus

api = flask.Blueprint(__name__, __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api.route('/trigger', methods=['POST'])
def trigger():
    logger.info('POST data: %s', flask.request.form)
    putioscanner.scan(int(flask.request.form.get('file_id', 0)))

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
    putioscanner.scan()

    response = {
        'route': '/full',
        'folder': {
            'id': 0,
        }
    }
    return flask.jsonify(response), 200


@api.route('/downloads')
def downloads():
    try:
        history_flag = flask.request.args['history']
        count = flask.request.args.get('count', 5)

        records = gethistoricaldownloads(count)
        out = {
            'data': [r.to_dict() for r in records]
        }

        return flask.json.dumps(out), 200
    except IndexError:
        pass

    try:
        in_progress_flag = flask.request.args['in_progress']

        records = getinprogressdownloads()

        out = {
            'data': [r.to_dict() for r in records]
        }
        
        return flask.json.dumps(out), 200
    except IndexError:
        pass

    return flask.json.dumps({}), 400


@orm.db_session
def gethistoricaldownloads(count):
    return orm.select(d for d in Download if d.status == DownloadStatus.done).order_by(orm.desc(Download.done_at)).limit(count).all()


@orm.db_session
def getinprogressdownloads():
    return orm.select(d for d in Download if d.status == DownloadStatus.in_progress).order_by(orm.desc(Download.done_at)).all()
