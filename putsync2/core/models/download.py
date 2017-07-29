import os
import logging
from enum import Enum
import datetime

from pony import orm

from ..db import db

logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    new = 'NEW'
    in_progress = 'IN_PROGRESS'
    done = 'DONE'
    failed = 'FAILED'


class Download(db.Entity):
    remote_file_id = orm.PrimaryKey(int)
    filepath = orm.Required(str)
    size = orm.Required(int)
    status = orm.Required(str, default=DownloadStatus.new.value)
    started_at = orm.Optional(datetime.datetime)
    done_at = orm.Optional(datetime.datetime)

    def markinprogress(self):
        self.status = DownloadStatus.in_progress.value
        self.started_at = datetime.datetime.now()

    def markdone(self):
        self.status = DownloadStatus.done.value
        self.done_at = datetime.datetime.now()

    def markfailed(self):
        self.status = DownloadStatus.failed.value

