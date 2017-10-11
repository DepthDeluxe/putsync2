import logging
from enum import Enum
import datetime

from pony import orm

from ..db import db

logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    new = 'new'
    in_progress = 'in_progress'
    done = 'done'
    failed = 'failed'


class Download(db.Entity):
    remote_file_id = orm.PrimaryKey(int, size=64)
    filepath = orm.Required(str)
    size = orm.Required(int, size=64)
    status = orm.Required(str, default=DownloadStatus.new.value)
    started_at = orm.Optional(datetime.datetime)
    done_at = orm.Optional(datetime.datetime)

    def markinprogress(self):
        self.status = DownloadStatus.in_progress.value
        self.started_at = datetime.datetime.utcnow()

    def markdone(self):
        self.status = DownloadStatus.done.value
        self.done_at = datetime.datetime.utcnow()

    def markfailed(self):
        self.status = DownloadStatus.failed.value
