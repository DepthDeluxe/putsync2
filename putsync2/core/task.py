from datetime import datetime
import enum
import logging

from weakref import WeakSet

logger = logging.getLogger(__name__)


class TaskStatus(enum.Enum):
    running = 'running'
    idle = 'idle'
    closed = 'closed'


class Task():
    task_registry = WeakSet()

    def __init__(self, name):
        self.name = name
        self.status = TaskStatus.idle
        self.started_at = None
        self.stopped_at = None

        self.task_registry.add(self)

    def running(self):
        if self.status != TaskStatus.idle:
            self.status = TaskStatus.running
            self.started_at = datetime.utcnow()

    def idle(self):
        if self.status != TaskStatus.idle:
            self.stopped_at = datetime.utcnow()

    def runtime(self):
        if self.status == TaskStatus.running:
            return datetime.utcnow() - self.started_at
        elif self.status == TaskStatus.idle:
            return self.stopped_at - self.started_at
        else:
            logger.error('Unknown state')
            return None

    def close(self):
        self.status = TaskStatus.closed

    def to_dict(self):
        return {
            'name': self.name,
            'status': self.status.value,
            'started_at': self.started_at,
            'stopped_at': self.stopped_at
        }

    @classmethod
    def instances(cls):
        return list(cls.task_registry)
