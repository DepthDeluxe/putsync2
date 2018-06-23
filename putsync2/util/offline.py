from threading import Thread

import schedule
import logging
import time
import random

from ..core.scanner import Scanner
from ..core.engine import Engine


logger = logging.getLogger(__name__)


class OfflineProcessor(object):
    def __init__(self, num_threads, putio_token, media_path,
                 disable_downloading, full_scan_interval):
        self._putio_token = putio_token
        self._media_path = media_path
        self._full_scan_interval = full_scan_interval
        self._disable_downloading = disable_downloading

        logger.info('Building the schedule thread')
        self._schedule_thread = Thread(target=self._schedule_thread_main,
                                       name='offline-schedule', daemon=True)

        logger.info(f'Creating the sync engine threads, will create '
                    f'{num_threads} threads')
        self._sync_engine_threads = [
            Thread(target=self._sync_engine_thread_main,
                   name=f'offline-sync_engine-{i}', args=(i,), daemon=True)
            for i in range(num_threads)
        ]

    def start(self):
        logger.info('Starting all threads')
        self._schedule_thread.start()
        for thread in self._sync_engine_threads:
            thread.start()

    def _schedule_thread_main(self):
        scanner = Scanner(self._putio_token, 'offline-scanner')
        schedule.every(self._full_scan_interval).minutes.do(scanner.scan)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def _sync_engine_thread_main(self, index):
        engine = Engine(self._putio_token, self._media_path,
                        self._disable_downloading,
                        name=f'offline-sync_engine-{index}')

        while True:
            engine.run()
            time.sleep(random.randrange(1, 10))
