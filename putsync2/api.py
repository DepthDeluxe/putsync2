import logging
import flask
import datetime

from pony.orm import db_session, select, count, sum, desc, max
import putiopy

from .core.scanner import Scanner
from .core.configuration import PutsyncConfig
from .core.models.download import Download, DownloadStatus
from .core.models.downloadattempt import DownloadAttempt, DownloadAttemptStatus

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

    downloads, count = getdownloadsfilterbystatus(status, page, page_size)
    out = {
        'count': count,
        'data': [d.to_dict() for d in downloads]
    }

    return flask.json.dumps(out)


@db_session
def getdownloadsfilterbystatus(status, page, page_size):
    status_obj = DownloadAttemptStatus.buildfromstring(status)

    query = select(
        a for a in DownloadAttempt
        if a.started_at == max(
            b.started_at for b in DownloadAttempt
            if a.download == b.download
        ) and a.status == status_obj.value
    ).order_by(
        desc(DownloadAttempt.done_at)
    )

    return query[page*page_size:(page+1)*page_size], query.count()


@api.route('/downloads/retry/<int:id>', methods=['POST'])
@db_session
def retrydownload(id):
    # mark as new again
    Download[id].new()
    data = Download[id].to_dict()

    return flask.jsonify({
        'data': data
    })


@api.route('/add', methods=['POST'])
def add():
    magnet_link = flask.request.json['magnet_link']

    client = putiopy.Client(PutsyncConfig().putio_token)
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


@db_session
def getbytesdownloaded():
    total_bytes = sum(
        d.size for d in Download if d.status == DownloadStatus.done.value
    )
    last_day_bytes = sum(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and max(d.attempts.started_at) > (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
    )
    last_month_bytes = sum(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and max(d.attempts.started_at) > (
            datetime.datetime.now() - datetime.timedelta(days=30)
        )
    )

    return total_bytes, last_day_bytes, last_month_bytes


@db_session
def getdownloadcount():
    total_count = count(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
    )
    last_day_count = count(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and max(d.attempts.started_at) > (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
    )
    last_month_count = count(
        d.size for d in Download
        if d.status == DownloadStatus.done.value
        and max(d.attempts.started_at) > (
            datetime.datetime.now() - datetime.timedelta(days=30)
        )
    )

    return total_count, last_day_count, last_month_count


@db_session
def getlastdownloadtime():
    t = max(
        attempt.done_at for attempt in DownloadAttempt
        if attempt.status == DownloadAttemptStatus.successful.value
    )

    return t
