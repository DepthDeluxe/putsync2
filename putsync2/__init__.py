import logging
import time
import os

from .core import db
from .core.offline import ConfiguredSchedulePool
from .core.configuration import set_config_filepath
from .webapp import app

logger = logging.getLogger(__name__)

config_path = os.environ.get('PUTSYNC_CONFIG', 'config.ini')

loggerformat =\
    '%(asctime)-15s [%(levelname)-8s] : %(name)-20s : %(thread)d : %(message)s'
logging.basicConfig(format=loggerformat, level=logging.INFO)
logger.warn(f'Log level set to INFO')
logger.warn(f'Using config file {config_path}')
set_config_filepath(config_path)
db.init()

webapp = app


def processor():
    logger.warn('Starting in processor mode')
    pool = ConfiguredSchedulePool()

    pool.start()

    while True:
        time.sleep(10)
