from threading import Lock
import logging

import putiopy

from putsync2.model.putioscanner import PutioScanner
from putsync2.model.download import DownloadThread
from putsync2.model.configuration import getputsyncconfig

logger = logging.getLogger(__name__)

download_queue = []
download_queue_lock = Lock()


def init():
    logger.info('Initializing putsync manager')
    config = getputsyncconfig()

    # create the threads and start them
    logger.info(f'Will spawn {config.download_threads} threads')
    threads = []
    for i in range(0, config.download_threads):
        threads.append(DownloadThread(download_queue, download_queue_lock))
    for thread in threads:
        thread.start()


def scan(id=0):
    config = getputsyncconfig()
    client = putiopy.Client(config.putio_token)

    logger.info(f'Starting scan of directory {id}')
    PutioScanner(id, download_queue, download_queue_lock).run(client)

    logger.info(f'Scan of {id} completed')
