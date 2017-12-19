import logging
import time
from threading import Thread
import os

from pony.orm import db_session, select, commit
import putiopy

from ..core.configuration import PutsyncConfig
from ..core.models.download import Download, DownloadStatus
from ..core.models.downloadattempt import DownloadAttempt, DownloadAttemptStatus

logger = logging.getLogger(__name__)


class Processor(object):
    @db_session
    @staticmethod
    def cleaninprocesssessions():
        attempts = select(
            a for a in DownloadAttempt
            if a.status == DownloadAttempt.in_progress.value
        )[:]

        for attempt in attempts:
            attempt.status = DownloadAttemptStatus.failed

    def continuous(self):
        logger.info('Starting download processor in continuous mode')
        while True:
            try:
                self.single()
            except ProcessorNoDownloadFoundError:
                logger.debug('No download found, sleeping')
                time.sleep(10)

    @db_session
    def _findnext(self):
        # find something that is not in progress
        try:
            return select(
                d for d in Download
                if d.status == DownloadStatus.new.value
            ).for_update()[:1][0]
        except IndexError:
            return None

    @db_session
    def single(self):
        download = self._findnext()
        if download is None:
            raise ProcessorNoDownloadFoundError(self)

        # create an attempt and immediately commit it
        download.attempted()
        attempt = DownloadAttempt(download=download)
        commit()

        try:
            self._attemptdownload(download)

            # if no uncaught exceptions, we are successful
            attempt.successful()
        except Exception:
            logger.exception('Uncaught exception when processing the download')

            attempt.failed()

    def _getremotefile(self, download):
        # also make sure to disable verification
        def _new_verify_file(*args, **kwargs):
            return True

        remote_file = putiopy.Client(PutsyncConfig().putio_token).File.get(download.remote_file_id)
        remote_file._verify_file = _new_verify_file
        logger.info('File verification disabled')

        return remote_file

    def _attemptdownload(self, download):
        remote_file = self._getremotefile(download)
        full_local_media_path = os.path.dirname(
            os.path.join(
                PutsyncConfig().media_path,
                download.filepath
            )
        )

        # remove the destination file if exists
        try:
            os.remove(full_local_media_path, str(download.name))
            logger.warn('Destination file exists, deleted it to perform download')
        except FileNotFoundError:
            logger.info('No destination file found')

        try:
            os.makedirs(full_local_media_path)
        except FileExistsError:
            logger.info(f'Folder {full_local_media_path} already exists')
            pass

        if PutsyncConfig().disable_downloading:
            logger.warn(f'Configured to disable real downloading')
        else:
            remote_file.download(dest=full_local_media_path)


class ProcessorError(Exception):
    def __init__(self, download_processor, message=None):
        if message is None:
            message = f'Generic download error with processor: '\
                      f'{download_processor}'

        super().__init__(message)
        self.download_processor = download_processor


class ProcessorFailedError(ProcessorError):
    def __init__(self, download_processor):
        message = 'Unable to download successfully'
        super().__init__(download_processor, message)


class ProcessorNoDownloadFoundError(ProcessorError):
    def __init__(self, download_processor):
        message = 'There is nothing to download'
        super().__init__(download_processor, message)


class ProcessorThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.processor = Processor()

    def run(self):
        logger.info(f'Starting processor thread {self}')
        self.processor.continuous()

    @staticmethod
    def buildmultiplefromconfigandstart():
        # clean current sessions in progress before starting
        Processor.cleaninprocesssessions()

        config = PutsyncConfig()

        threads = []
        for i in range(0, config.processor_threads):
            processor = ProcessorThread()
            processor.start()
            threads.append(processor)

        return threads


if __name__ == '__main__':
    from . import db
    from .configuration import Config

    print('-----')
    loggerformat =\
        '%(asctime)-15s [%(levelname)s] : %(name)s : %(thread)d : %(message)s'
    logging.basicConfig(format=loggerformat, level=logging.INFO)
    logger.warn(f'Log level set to {logging.INFO}')

    Config.setconfigfilepath('./dev-config.ini')

    db.init()
    threads = ProcessorThread.buildmultiplefromconfigandstart()

    while True:
        time.sleep(1)
