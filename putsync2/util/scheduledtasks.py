from threading import Thread
import time
import logging

import schedule

from ..core import putioscanner
from ..core.configuration import getputsyncconfig

logger = logging.getLogger(__name__)


def fullscan():
    logger.info('Performing periodic full scan')

    putioscanner.scan()


class SchduledTaskThread(Thread):
    def __init__(self, *args, **kwargs):
        super(SchduledTaskThread, self).__init__(*args, **kwargs)
        self.setDaemon(True)
        logger.info('Starting up scheduled task thread')

        config = getputsyncconfig()

        logger.info(
            f'Scheduling full scan to happen every '
            f'{config.full_scan_interval_minutes} minutes'
        )
        schedule.every(config.full_scan_interval_minutes).minutes.do(fullscan)

    def run(self):
        logger.info('Started ScheduledTaskThread')
        while True:
            schedule.run_pending()
            time.sleep(1)
