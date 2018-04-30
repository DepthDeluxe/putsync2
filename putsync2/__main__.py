import logging

from .core.models.file import FileCollection
from .core import db
from .core.offline import ConfiguredSchedulePool
from .webapp import app

logger = logging.getLogger(__name__)

with db.SessionContext() as session:
    FileCollection(session).delete_pending()

pool = ConfiguredSchedulePool()
pool.start()
app.run(port=9000)
