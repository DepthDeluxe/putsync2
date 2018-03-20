from datetime import datetime, timedelta
import logging
import enum
import functools

from sqlalchemy import Column, Integer, String, DateTime, Enum, func


from ..db import Base
from ..configuration import config_instance

logger = logging.getLogger(__name__)


class FileStatus(enum.Enum):
    new = 'new'
    in_progress = 'in_progress'
    done = 'done'


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    putsync_id = Column(Integer)
    filepath = Column(String)
    size = Column(Integer)
    status = Column(Enum(FileStatus), default=FileStatus.new)
    started_at = Column(DateTime)
    done_at = Column(DateTime)
    attempt_count = Column(Integer, default=0)

    def move(self, new_filepath):
        pass

    def start(self):
        self.status = FileStatus.in_progress
        self.started_at = datetime.utcnow()
        self.done_at = None
        self.attempt_count += 1

    def done(self):
        self.status = FileStatus.done
        self.done_at = datetime.utcnow()

    def fail(self):
        self.status = FileStatus.new
        self.done_at = datetime.utcnow()

    @functools.lru_cache(maxsize=32)
    def remotefile(self):
        # we want to disable file verification becuase it takes a very long
        # time to run on a Raspberry Pi.  We want to maximize the download
        # rate.
        def _new_verify_file(*args, **kwargs):
            logger.info('File verification called, running stub instead')
            return True

        remote_file = config_instance().getclient().File.get(
            self.putsync_id
        )
        remote_file._verify_file = _new_verify_file

        return remote_file


class FileCollection(object):
    def __init__(self, session):
        self._session = session

    def add(self, remote_file, filepath):
        existing = self._getexistingdownload(remote_file.id)
        if existing is None:
            logger.info('Remote file does not currently exist so we will add')

            file = File(
                putsync_id=remote_file.id,
                filepath=filepath,
                size=remote_file.size
            )
            self._session.add(file)

            return file
        else:
            logger.warn('Remote file already exists in the collection')
            return existing

    def _getexistingdownload(self, remote_id):
        return self._session.query(File)\
            .filter_by(putsync_id=remote_id)\
            .first()

    def getbyid(self, id_):
        return self._session.query(File).get(id_)

    def query(self, status=FileStatus.done, page=1, page_size=10):
        if isinstance(status, str):
            status = FileStatus(status)

        query = self._session.query(File)\
            .filter_by(status=status)\
            .offset(page * page_size)\
            .limit(page_size)

        return query.all(), query.count()

    def inprogress(self, page=1, page_size=10):
        return self.query(
            status=FileStatus.in_progress,
            page=page,
            page_size=page_size
        )

    def countndays(self, n):
        result = self._session.query(func.count(File.id))\
            .filter(
                File.status == FileStatus.done and
                File.done_at > (datetime.utcnow() - timedelta(days=n))
            ).first()[0]

        logger.info(f'Downloaded {result} files in past {n} days')
        return result

    def bytesndays(self, n):
        result = self._session.query(func.sum(File.size))\
            .filter(
                File.status == FileStatus.done and
                File.done_at > (datetime.utcnow() - timedelta(days=n))
            ).first()[0]

        logger.info(f'Downloaded {result} bytes in past {n} days')
        return result
