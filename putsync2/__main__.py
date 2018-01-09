import logging
import time

from .core import db
from .core.configuration import Config
from .core.offline import ConfiguredSchedulePool
from .webapp import app

from pony.orm import db_session

logger = logging.getLogger(__name__)

pool = ConfiguredSchedulePool()
pool.start()
app.run(port=9000)
