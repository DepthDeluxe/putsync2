import logging
from datetime import datetime, timedelta

from pony.orm import select, count, db_session, sum, desc

from .models.file import File
from .models.syncattempt import SyncAttempt


logger = logging.getLogger(__name__)


@db_session
def add(remote_file, filepath):
    existing = _getexistingdownload(remote_file.id)
    if existing is None:
        logger.info('Remote file does not currently exist so we will add')

        file = File(
            remote_file_id=remote_file.id,
            filepath=filepath,
            size=remote_file.size
        )

        return file
    else:
        logger.warn('Remote file already exists in the collection')
        return existing


@db_session
def _getexistingdownload(remote_id):
    return select(
        f for f in File
        if f.remote_file_id == remote_id
    ).first()


@db_session
def getbyid(id):
    return File[id]


@db_session
def synchistory(status=SyncAttempt.Status.successful, page=1, page_size=10):
    query = select(
        f for f in File
        if count(
            a for a in f.attempts
            if a.status == status
        ) > 0
    )

    return query.page(page, page_size), query.count()


@db_session
def inprogress(page=1, page_size=10):
    return synchistory(
        status=SyncAttempt.Status.in_progress,
        page=page,
        page_size=page_size
    )


@db_session
def countndays(n):

    return select(
        count(f) for f in File
        if count(
            a for a in SyncAttempt
            if a.status == SyncAttempt.Status.successful
            and a.finished_at > (datetime.utcnow() - timedelta(days=n))
        ) > 0
    ).first()


@db_session
def bytesndays(n):
    return select(
        sum(f.size) for f in File
        if count(
            a for a in SyncAttempt
            if a.status == SyncAttempt.Status.successful
            and a.finished_at > (datetime.utcnow() - timedelta(days=n))
        ) > 0
    ).first()


@db_session
def pendingfiles():
    attempts = select(
        a for a in SyncAttempt
        if a.status == SyncAttempt.Status.in_progress
    ).order_by(desc(SyncAttempt.started_at))[:]

    return list(map(lambda a: a.file, attempts))


@db_session
def nextpending():
    # find something that doesn't have any successful attempts
    # do not wait for the row lock, will throw exception which
    # will trigger retry
    for i in range(10):
        file = select(
            f for f in File
            if count(
                a for a in f.attempts
                if a.status == SyncAttempt.Status.successful
            ) == 0
        ).for_update().first()

        if file is None:
            return None

        in_progrsss_count = len([
            a for a in file.attempts
            if a.status == SyncAttempt.Status.in_progress
        ]) > 0

        if in_progrsss_count == 0:
            logger.info(f'Found file, took {i} attempts')
            return file


@db_session
def cleaninprogressattempts():
    logger.info(
        'Cleaning existing sessions, will typically be called on '
        'initialization'
    )
    attempts = select(
        a for a in SyncAttempt
        if a.status == SyncAttempt.Status.in_progress
    )[:]

    for attempt in attempts:
        attempt.failed('Cancelling due to start-up')
