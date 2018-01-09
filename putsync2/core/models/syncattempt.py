from enum import Enum
from datetime import datetime

from pony.orm import PrimaryKey, Required, Optional

from ..db import PutsyncEntity


class SyncAttempt(PutsyncEntity):
    class Status(object):
        in_progress = 'in_progress'
        successful = 'successful'
        failed = 'failed'

    file = Required('File')
    started_at = Required(datetime, default=datetime.utcnow())
    finished_at = Optional(datetime)
    status = Required(str, default=Status.in_progress)
    error_message = Optional(str)

    def failed(self, message=None):
        self.error_message = message
        self.status = self.Status.failed
        self.finished_at = datetime.utcnow()

    def successful(self):
        self.status = self.Status.successful
        self.finished_at = datetime.utcnow()
