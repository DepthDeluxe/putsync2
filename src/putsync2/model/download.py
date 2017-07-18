import os
import time
import logging
from enum import Enum

import putsync2.putioscanner
import putsync2.util
import putsync2.model.statestore
from putsync2.model.configuration import getputsyncconfig

logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    new = 'NEW'
    in_progress = 'IN_PROGRESS'
    done = 'DONE'
    failed = 'FAILED'


class Download(object):
    def __init__(self, remote_file, path):
        self.remote_file = remote_file
        self.path = path

        self.status = DownloadStatus.new

    def __eq__(self, other):
        return self.remote_file.id == other.remote_file.id

    def __disable_file_verification(self):
        def __new_verify_file(*args, **kwargs):
            return True

        self.remote_file._verify_file = __new_verify_file
        logger.info('File verification disabled')

    def markinprogress(self):
        self.status = DownloadStatus.in_progress

    def markdone(self):
        self.status = DownloadStatus.done

    def markfailed(self):
        self.status = DownloadStatus.failed

    def run(self):
        config = getputsyncconfig()

        self.__disable_file_verification()
        logger.info(f'Starting download of {self.remote_file.name}')

        full_local_media_path = os.path.join(config.media_path, self.path)
        util.mkdir_p(full_local_media_path)

        if config.disable_downloading:
            logger.warn(f'Not actually downloading {self.remote_file.name}, configured to disable real downloading')
        else:
            self.remote_file.download(dest=full_local_media_path)

        logger.info(f'{self.remote_file.name} download successful, committing result')
        self.__commit_done()

    def __commit_done(self):
        statestore.commit(self)

        logger.info(f'{self.remote_file.name} committed')
