from datetime import datetime
import enum
import logging

from sqlalchemy import Column, String, DateTime, Enum

from ..db import Base

logger = logging.getLogger(__name__)


class TaskStatus(enum.Enum):
    running = 'running'
    idle = 'idle'


class Task(Base):
    __tablename__ = 'tasks'

    name = Column(String, primary_key=True)
    status = Column(Enum(TaskStatus))
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)

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
