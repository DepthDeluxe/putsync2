import time
from threading import Thread
import logging

from pony import orm

from ..core.configuration import getputsyncconfig
from ..core import downloadprocessor
from ..core.models.download import Download, DownloadStatus


logger = logging.getLogger(__name__)


def createdownloadthreads():
    logger.info('Initializing putsync manager')
    config = getputsyncconfig()

    # create the threads and start them
    logger.info(f'Will spawn {config.download_threads} threads')
    threads = []
    for i in range(0, config.download_threads):
        threads.append(DownloadThread())
    for thread in threads:
        thread.start()


class DownloadThread(Thread):
    def __init__(self, *args, **kwargs):
        super(DownloadThread, self).__init__(*args, **kwargs)
        self.setDaemon(True)

    def run(self):
        while True:
            while self.loop():
                pass
            
            logger.info('No downloads found, sleeping for 10 seconds')
            time.sleep(10)

    @orm.db_session
    def loop(self):
        download = self.__getnextdownload()
        if download is not None:
            downloadprocessor.processdownload(download)
            return True
        else:
            return False


    def __getnextdownload(self):
        return orm.select(d for d in Download if d.status == DownloadStatus.new.value).first()
