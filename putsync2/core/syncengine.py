import logging
import os
from datetime import datetime

from pony.orm import db_session, commit

from .models.file import FileCollection, File, FileStatus
from .configuration import PutsyncConfig
from .models.file import File

logger = logging.getLogger(__name__)


class SyncEngine(object):
    def syncnextpendingfile(self):
        try:
            with db_session(serializable=True):
                file = File.get(status=FileStatus.new)

                if file is None:
                    logger.warn('No file found to sync')
                    return None

                file.status = FileStatus.syncing
                file.started_at = datetime.utcnow()

                id_ = file.id
                remote_file = file.remotefile()
                filepath = file.filepath
        except Exception as e:
            import ipdb; ipdb.set_trace()
            logger.exception('Some uncaught exception in above')

        full_filepath = os.path.join(
            PutsyncConfig().media_path,
            filepath
        )

        try:
            self._attempt(remote_file, full_filepath)
            failed = False
        except Exception as e:
            logger.exception('Uncaught exception when processing the download')
            failed = True

        with db_session:
            if failed:
                File[id_].fail()
            else:
                File[id_].done()

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
