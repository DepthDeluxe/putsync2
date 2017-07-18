import time
from threading import Thread, Lock
import logging

import putiopy

import putioscanner
from model.configuration import getputsyncconfig
from model.download import DownloadStatus

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

        self.queue, self.queue_lock = putioscanner.getqueueandlock()

    def run(self):
        while True:
            try:
                self.queue_lock.acquire()
                try:
                    next_download = self.__get_next_download_and_mark_in_progress_or_return_none()
                except Exception as e:
                    raise e
                finally:
                    self.queue_lock.release()

                if next_download:
                    logger.info('Found something to download')
                    next_download.run()
                    next_download.markdone()
                    self.queue.remove(next_download)
                else:
                    logger.info('Nothing found to download, sleeping for 10 seconds')
                    time.sleep(10)
            except Exception:
                logger.exception('Error encountered in download loop')

    def __get_next_download_and_mark_in_progress_or_return_none(self):
        try:
            download = [download for download in self.queue if download.status == DownloadStatus.new][0]
            download.markinprogress()

            return download
        except IndexError:
            return None
