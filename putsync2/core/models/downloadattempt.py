from enum import Enum
from datetime import datetime

from pony.orm import PrimaryKey, Required, Optional

from ..db import db


class DownloadAttemptStatus(Enum):
    failed = 0
    in_progress = 1
    successful = 2

    def __str__(self):
        if self.value == DownloadAttemptStatus.failed:
            return 'failed'
        elif self.value == DownloadAttemptStatus.in_progress:
            return 'in_progress'
        else:
            return 'successful'

    @staticmethod
    def buildfromstring(string):
        if string == 'failed':
            return DownloadAttemptStatus.failed
        elif string == 'in_progress':
            return DownloadAttemptStatus.in_progress
        else:
            return DownloadAttemptStatus.successful


class DownloadAttempt(db.Entity):
    download = Required('Download')
    started_at = Required(datetime, default=datetime.utcnow())
    done_at = Optional(datetime)
    status = Required(int, default=DownloadAttemptStatus.in_progress.value)

    def failed(self):
        self.status = DownloadAttemptStatus.failed.value
        self.done_at = datetime.utcnow()

    def successful(self):
        self.status = DownloadAttemptStatus.successful.value
        self.done_at = datetime.utcnow()

    def to_dict(self):
        attempt_dict = {
            'download': self.download.id,
            'started_at': self.started_at,
            'done_at': self.done_at,
            'status': str(self.status)
        }

        return {**attempt_dict, **self.download.to_dict()}
