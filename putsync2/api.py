import logging
import flask
import datetime

from pony import orm
import putiopy

from .core import putioscanner
from .core.configuration import getputsyncconfig
from .core.models.download import Download, DownloadStatus

from .core.db import db

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
    status = flask.request.args.get('status', 'done')
    page = flask.request.args.get('page', 0, type=int)
    page_size = flask.request.args.get('page-size', 25, type=int)

    downloads, count = getdownloadsfilterbystatus(status, page, page_size)
    out = {
        'count': count,
        'data': [d.to_dict() for d in downloads]
        }

    return flask.json.dumps(out)


@orm.db_session
def getdownloadsfilterbystatus(status, page, page_size):
    data = orm.select(d for d in Download if d.status == status)\
            .order_by(
                orm.desc(Download.done_at))[
                    page*page_size:(page+1)*page_size
                ]
    count = orm.select(
        orm.count(d) for d in Download if d.status == status
    ).first()

    return data, count


@api.route('/add', methods=['POST'])
def add():
    magnet_link = flask.request.json['magnet_link']

    client = putiopy.Client(getputsyncconfig().putio_token)
    client.Transfer.add_url(magnet_link)

    return 'Accepted', 202


@api.route('/statistics')
def statistics():
    # get bytes downloaded
    total_bytes, last_day_bytes, last_month_bytes = getbytesdownloaded()
    # get number of downloads
    total_count, last_day_count, last_month_count = getdownloadcount()
    # get last download time
    last_download_time = getlastdownloadtime()
    # get average download rate
    rate = getaveragedownloadrate()

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
            'rate': {'1day': rate}
            }
        })


@orm.db_session
def getbytesdownloaded():
    total_bytes = orm.sum(
        d.size for d in Download if d.status == DownloadStatus.done.value
    )
    last_day_bytes = orm.sum(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and d.started_at > (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
    )
    last_month_bytes = orm.sum(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and d.started_at > (
            datetime.datetime.now() - datetime.timedelta(days=30)
        )
    )

    return total_bytes, last_day_bytes, last_month_bytes


@orm.db_session
def getdownloadcount():
    total_count = orm.count(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
    )
    last_day_count = orm.count(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and d.started_at > (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
    )
    last_month_count = orm.count(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and d.started_at > (
            datetime.datetime.now() - datetime.timedelta(days=30)
        )
    )

    return total_count, last_day_count, last_month_count


@orm.db_session
def getlastdownloadtime():
    t = orm.max(
        d.done_at for d in Download
        if d.status == DownloadStatus.done.value
    )

    return t


@orm.db_session
def getaveragedownloadrate():
    rate = db.select('''
    AVG(size / ((julianday(done_at) - julianday(started_at)) * 86400.0))
FROM
    Download
WHERE
    status = 'done' ''')

    return rate
