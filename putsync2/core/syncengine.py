import logging
import os

from pony.orm import db_session, commit

from . import filecollection
from .configuration import PutsyncConfig
from .models.syncattempt import SyncAttempt

logger = logging.getLogger(__name__)


class SyncEngine(object):
    @db_session
    def syncnextpendingfile(self):
        self.current_file = filecollection.nextpending()
        if self.current_file is None:
            logger.warn('Nothing found to sync')
            return None

        self.current_attempt = SyncAttempt(file=self.current_file)
        commit()

        try:
            self._attempt()

            # if no uncaught exceptions, we are successful
            self.current_attempt.successful()
        except Exception as e:
            logger.exception('Uncaught exception when processing the download')

            self.current_attempt.failed(str(e))

        return self.current_attempt, self.current_file

    @db_session
    def _attempt(self):
        remote_file = self.current_file.remotefile()
        full_filepath = os.path.join(
            PutsyncConfig().media_path,
            self.current_file.filepath
        )
        parent_folderpath = os.path.dirname(full_filepath)

        # remove the destination file if exists
        try:
            os.remove(full_filepath)
            logger.warn(
                'Destination file exists, deleted it to perform download'
            )
        except FileNotFoundError:
            logger.info('No destination file found')

        # make folder structure
        try:
            os.makedirs(parent_folderpath)
        except FileExistsError:
            logger.info(f'Folder {parent_folderpath} already exists')

        if PutsyncConfig().disable_downloading:
            logger.warn(f'Configured to disable real downloading')
        else:
            remote_file.download(dest=parent_folderpath)
