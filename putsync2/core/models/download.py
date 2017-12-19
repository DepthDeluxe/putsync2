import logging
from enum import Enum
import datetime

from pony.orm import PrimaryKey, Required, Set, select

from ..db import db
from .downloadattempt import DownloadAttempt

logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    new = 'new'
    done = 'done'
    attempted = 'attempted'


class Download(db.Entity):
    remote_file_id = Required(int, size=64)
    filepath = Required(str)
    size = Required(int, size=64)
    status = Required(str, default=DownloadStatus.new.value)
    attempts = Set(DownloadAttempt)

    def new(self):
        self.status = DownloadStatus.new.value

    def attempted(self):
        self.status = DownloadStatus.attempted.value

    def done(self):
        self.status = DownloadStatus.done.value

    def done_at(self):
        if self.status == DownloadStatus.done.value:
            max([attempt.done_at for attempt in self.attempts])
        else:
            return None
