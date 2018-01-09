from threading import Thread
from queue import Queue

import schedule
import logging
import time

from . import filecollection
from .configuration import PutsyncConfig
from .scanner import Scanner
from .syncengine import SyncEngine


logger = logging.getLogger(__name__)


class OfflineScanner(object):
    def __init__(self, interval_minutes):
        self._scanner = Scanner()
        self.interval = interval_minutes

    def run(self):
        logger.info('Running scheduled offline scanner task')
        try:
            self._scanner.scan()
        except Exception:
            logger.exception('Uncaught exception when running OfflineScanner')

    def getschedule(self):
        return schedule.every(
            self.interval
        ).minutes


class OfflineSyncEngine(object):
    def __init__(self, interval_seconds):
        self._engine = SyncEngine()
        self.interval = interval_seconds

    def run(self):
        logger.debug('Running processor task')
        try:
            while self._engine.syncnextpendingfile() is not None:
                pass
        except Exception:
            logger.exception(
                'Uncaught exception when running OfflineProcessor'
            )

    def getschedule(self):
        return schedule.every(self.interval).seconds


class SchedulePool(object):
    def __init__(self, pool_size=5):
        self._runnables = []
        self._queue = Queue()

        self._control_thread = Thread(
            name='OfflineThread-Control',
            target=self._controlthreadtask,
            daemon=True
        )

        self._worker_threads = []
        for i in range(pool_size):
            self._worker_threads.append(
                Thread(
                    name=f'OfflineThread-{i}',
                    target=self._workthreadtask,
                    daemon=True
                )
            )

    def start(self):
        logger.info('Starting up all offline threads')
        for t in self._worker_threads:
            t.start()

        self._control_thread.start()

    def addrunnable(self, runnable):
        logger.info(f'Scheduling {runnable}')

        runnable.getschedule().do(self._submitrunnable, runnable)
        self._runnables.append(runnable)

    def _workthreadtask(self):
        while True:
            runnable = self._queue.get()

            try:
                runnable.run()
            except Exception:
                logger.exception(f'Uncaught exception in runnable {runnable}')

    def _controlthreadtask(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def _submitrunnable(self, runnable):
        self._queue.put(runnable)


class ConfiguredSchedulePool(object):
    def __init__(self):
        filecollection.cleaninprogressattempts()

        config = PutsyncConfig()
        tasks_count = config.processor_threads

        self._pool = SchedulePool(pool_size=tasks_count)
        self._scanner = OfflineScanner(
            interval_minutes=config.full_scan_interval_minutes
        )
        self._engines = []
        for i in range(config.processor_threads):
            self._engines.append(OfflineSyncEngine(interval_seconds=5))

        self._pool.addrunnable(self._scanner)
        for p in self._engines:
            self._pool.addrunnable(p)

    def start(self):
        self._pool.start()
