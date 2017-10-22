import logging
from threading import Thread
from queue import Queue
import os

from pony.orm import db_session, select
import putiopy

from ..core.configuration import getputsyncconfig
from ..core.models.download import Download, DownloadStatus

logger = logging.getLogger(__name__)


def createprocessor():
    return DownloadThreadPool(getputsyncconfig().download_threads)


class Worker(Thread):
    def __init__(self, tasks):
        super().__init__(daemon=True)
        self.tasks = tasks

    def run(self):
        logger.info(f'Starting worker {self}')
        while True:
            download_id = self.tasks.get()

            try:
                processdownload(download_id)
            finally:
                self.tasks.task_done()


class DownloadThreadPool(object):
    def __init__(self, num_threads):
        logger.info(
            'Initializing DownloadThreadPool object,'
            ' will create and start threads'
        )
        self.tasks = Queue()
        self.workers = []
        for i in range(num_threads):
            self.workers.append(Worker(self.tasks))
        for worker in self.workers:
            worker.start()

    def add_download(self, download_id):
        self.tasks.put(download_id)


def processdownload(id):
    if not checkdownloadvalidandmarkinprogress(id):
        return

    try:
        __processdownloadandpossiblyfail(id)
    except Exception:
        logger.exception(
            'Unable to process download in a timely manner, marking as failed'
        )
        markfaileddownload(id)


def __processdownloadandpossiblyfail(id):
    # get the remote file and disable file verification because it is slow
    remote_file = putiopy.Client(getputsyncconfig().putio_token).File.get(id)
    __disable_file_verification(remote_file)

    logger.info(f'Starting download of {remote_file.name}')

    with db_session:
        full_local_media_path = os.path.dirname(
            os.path.join(
                getputsyncconfig().media_path,
                Download[id].filepath
            )
        )
        try:
            os.makedirs(full_local_media_path)
        except FileExistsError:
            logger.info(f'Folder {full_local_media_path} already exists')
            pass

    if getputsyncconfig().disable_downloading:
        logger.warn(f'Configured to disable real downloading')
    else:
        remote_file.download(dest=full_local_media_path)

    # commit the results
    with db_session:
        Download[id].markdone()
    logger.info(f'{remote_file.name} download successful')


@db_session
def checkdownloadvalidandmarkinprogress(id):
    download = Download.get_for_update(id)

    if download.status != DownloadStatus.new.value:
        logger.debug(
            f'Attempting to download {download.remote_file_id}'
            f' when in {download.status} state, skipping'
        )
        return False
    else:
        download.markinprogress()
        return True


def __disable_file_verification(remote_file):
    def __new_verify_file(*args, **kwargs):
        return True

    remote_file._verify_file = __new_verify_file
    logger.info('File verification disabled')


@db_session
def getnextdownloadid():
    try:
        return select(
            d for d in Download
            if d.status == DownloadStatus.new.value
        ).first().remote_file_id
    except AttributeError:
        return None


@db_session
def markfaileddownload(id):
    Download.get_for_update(id).markfailed()
