import logging
import sys

from .core.configuration import getputsyncconfig, getserverconfig,\
        setconfigfilepath
from .util.purger import purgeinprogressdownloads
from .core.downloadprocessor import createprocessor
from .util.scheduledtasks import SchduledTaskThread
from .webapp import app

from .core import db

logger = logging.getLogger(__name__)
loggerformat =\
    '%(asctime)-15s [%(levelname)s] : %(name)s : %(thread)d : %(message)s'


def main():
    if len(sys.argv) < 2:
        print(
            'Need to specify configuration file, '
            'format is : main.py [file.ini]'
        )
        sys.exit(1)

    # setup configuration and load it
    setconfigfilepath(sys.argv[1])
    setuplogging()
    config = getserverconfig()

    db.init()

    # we want to purge anything in-progress on start because
    # it won't properly resume on start again
    purgeinprogressdownloads()
    createprocessor()
    SchduledTaskThread().start()

    logger.info('Loaded configuration')
    logger.info('Server host %s port %s', config.host, config.port)
    app.run(host=config.host, port=config.port)


def setuplogging():
    config = getputsyncconfig()
    if config.log_level == 'WARN':
        level = logging.WARN
    elif config.log_level == 'INFO':
        level = logging.INFO
    elif config.log_level == 'DEBUG':
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format=loggerformat, level=level)
    logger.warn(f'Log level set to {level}')


if __name__ == '__main__':
    main()
