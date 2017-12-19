import logging
import time
import os

from .core import db
from .core.configuration import Config
from .core.processor import ProcessorThread
from .core.scanner import ScannerThread
from .webapp import app

logger = logging.getLogger(__name__)

config_path = os.environ.get('PUTSYNC_CONFIG', 'config.ini')

print('-----')
loggerformat =\
    '%(asctime)-15s [%(levelname)-8s] : %(name)-20s : %(thread)d : %(message)s'
logging.basicConfig(format=loggerformat, level=logging.INFO)
logger.warn(f'Log level set to INFO')
logger.warn(f'Using config file {config_path}')
Config.setconfigfilepath(config_path)
db.init()


def processor():
    logger.warn('Starting up in processor mode')
    ProcessorThread.buildmultiplefromconfigandstart()
    ScannerThread().start()

    while True:
        time.sleep(1)


webapp = app
