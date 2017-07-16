import logging
import sys

from putsync2.model.configuration import getserverconfig, setconfigfilepath
import putsync2.model.manager as manager

from .webapp import app
from .scheduledtasks import SchduledTaskThread

logger = logging.getLogger(__name__)
loggerformat = '%(asctime)-15s [%(levelname)s] : %(name)s : %(thread)d : %(message)s'


def main():
    logging.basicConfig(format=loggerformat, level=logging.INFO)

    if len(sys.argv) < 2:
        logger.error('Need to specify configuration file, format is : main.py [file.ini]')
        sys.exit(1)

    setconfigfilepath(sys.argv[1])
    config = getserverconfig()

    manager.init()

    SchduledTaskThread().start()

    logger.info('Loaded configuration')
    logger.info('Server host %s port %s', config.host, config.port)
    app.run(host=config.host, port=config.port)

if __name__ == '__main__':
    main()
