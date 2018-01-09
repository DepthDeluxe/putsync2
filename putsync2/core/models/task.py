from datetime import datetime
import logging

from pony.orm import PrimaryKey, Required, Optional

from ..db import PutsyncEntity

logger = logging.getLogger(__name__)


class Task(PutsyncEntity):
    class Status(object):
        running = 'running'
        idle = 'idle'

    name = PrimaryKey(str)
    status = Required(str, default=Status.idle)
    started_at = Optional(datetime)
    stopped_at = Optional(datetime)

    def running(self):
        if self.status != self.Status.idle:
            self.status = self.Status.running
            self.started_at = datetime.utcnow()

    def idle(self):
        if self.status != self.Status.idle:
            self.stopped_at = datetime.utcnow()

    def runtime(self):
        if self.status == self.Status.running:
            return datetime.utcnow() - self.started_at
        elif self.status == self.Status.idle:
            return self.stopped_at - self.started_at
        else:
            logger.error('Unknown state')
            return None
