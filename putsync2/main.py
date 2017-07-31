import logging
import sys

from .core.configuration import getserverconfig, setconfigfilepath
from .util.downloadthread import createdownloadthreads
from .util.scheduledtasks import SchduledTaskThread
from .webapp import app

from .core import db

logger = logging.getLogger(__name__)
loggerformat = '%(asctime)-15s [%(levelname)s] : %(name)s : %(thread)d : %(message)s'


def main():
    logging.basicConfig(format=loggerformat, level=logging.INFO)

    if len(sys.argv) < 2:
        logger.error('Need to specify configuration file, format is : main.py [file.ini]')
        sys.exit(1)

    # setup configuration and load it
    setconfigfilepath(sys.argv[1])
    config = getserverconfig()

    db.init() 
    createdownloadthreads()
    SchduledTaskThread().start()

    logger.info('Loaded configuration')
    logger.info('Server host %s port %s', config.host, config.port)
    app.run(host=config.host, port=config.port)

if __name__ == '__main__':
    main()
