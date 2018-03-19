from datetime import datetime, timedelta
import logging
from enum import Enum

from pony.orm import Required, Optional, db_session, select, count, \
                     sum, desc

from ..db import PutsyncEntity
from ..configuration import PutsyncConfig

logger = logging.getLogger(__name__)


class FileStatus(Enum):
    new = 'new'
    in_progress = 'in_progress'
    done = 'new'


class File(PutsyncEntity):
    putsync_id = Required(int, size=64)
    filepath = Required(str)
    size = Required(int, size=64)
    status = Required(FileStatus, default=FileStatus.new)
    started_at = Optional(datetime)
    done_at = Optional(datetime)
    attempt_count = Required(int, default=0)

    def move(self, new_filepath):
        pass

    def start(self):
        self.status = FileStatus.syncing
        self.started_at = datetime.utcnow()
        self.done_at = None
        self.attempt_count += 1

    def done(self):
        self.status = FileStatus.done
        self.done_at = datetime.utcnow()

    def fail(self):
        self.status = FileStatus.new
        self.done_at = datetime.utcnow()

    def remotefile(self):
        # we want to disable file verification becuase it takes a very long
        # time to run on a Raspberry Pi.  We want to maximize the download
        # rate.
        def _new_verify_file(*args, **kwargs):
            logger.info('File verification called, running stub instead')
            return True

        remote_file = PutsyncConfig().getclient().File.get(
            self.putsync_id
        )
        remote_file._verify_file = _new_verify_file

        return remote_file


class FileCollection(object):
    @db_session
    def add(self, remote_file, filepath):
        existing = self._getexistingdownload(remote_file.id)
        if existing is None:
            logger.info('Remote file does not currently exist so we will add')

            file = File(
                putsync_id=remote_file.id,
                filepath=filepath,
                size=remote_file.size
            )

            return file
        else:
            logger.warn('Remote file already exists in the collection')
            return existing

    @db_session
    def _getexistingdownload(self, remote_id):
        return select(
            f for f in File
            if f.putsync_id == remote_id
        ).first()

    @db_session
    def getbyid(self, id_):
        return File[id_]

    @db_session
    def query(self, status=FileStatus.done.value, page=1, page_size=10):
        import ipdb; ipdb.set_trace()
        # TODO(colin): implement enum support
        query = select(
            f for f in File
            if f.status == status
        )

        return query.page(page, page_size), query.count()

    @db_session
    def inprogress(self, page=1, page_size=10):
        return self.query(
            status=FileStatus.syncing,
            page=page,
            page_size=page_size
        )

    @db_session
    def countndays(n):
        logger.error('Not implemented')
        return 0

    @db_session
    def bytesndays(n):
        logger.error('Not implemented')
        return 0
