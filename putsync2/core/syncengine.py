import logging
import os

from pony.orm import db_session, commit

from . import filecollection
from .configuration import PutsyncConfig
from .models.file import File
from .models.syncattempt import SyncAttempt

logger = logging.getLogger(__name__)


class SyncEngine(object):
    def syncnextpendingfile(self):
        with db_session:
            file = filecollection.nextpending()
            if file is None:
                logger.warn('Nothing found to sync')
                return None

            attempt = SyncAttempt(file=file)
            commit()

            file_id = file.id
            attempt_id = attempt.id

            remote_file = File[file_id].remotefile()
            full_filepath = os.path.join(
                PutsyncConfig().media_path,
                File[file_id].filepath
            )

        try:
            self._attempt(remote_file, full_filepath)

            # if no uncaught exceptions, we are successful
            with db_session:
                SyncAttempt[attempt_id].successful()
        except Exception as e:
            logger.exception('Uncaught exception when processing the download')

            with db_session:
                SyncAttempt[attempt_id].failed(str(e))

        return file_id, attempt_id

    def _attempt(self, remote_file, full_filepath):
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
