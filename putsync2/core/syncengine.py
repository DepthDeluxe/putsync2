import logging
import os
from datetime import datetime

from sqlalchemy.orm.session import make_transient

from .db import SessionContext, Session
from .models.file import FileCollection, File, FileStatus
from .configuration import config_instance
from .models.file import File

logger = logging.getLogger(__name__)


class SyncEngine(object):
    def syncnextpendingfile(self):
        with SessionContext() as session:
            file = session.query(File)\
                .filter_by(status=FileStatus.new)\
                .first()

            if file is None:
                logger.warn('No file found to sync')
                return None

            logger.info(f'Processing file {file.id}')
            file.start()

            id_ = file.id

        # get transient copy from DB, need transient so the long-running
        # download doesn't eat a session
        with SessionContext(autocommit=False) as session:
            file = session.query(File).get(id_)
            make_transient(file)

        try:
            self._attempt(file)
            file.done()
        except Exception as e:
            logger.exception('Exception {e} fired when processing file {file.filepath}')
            file.fail()

        # remerge detached object back with session
        with SessionContext() as session:
            session.merge(file)

            return file.id

    def _attempt(self, file):
        full_filepath = os.path.join(
            config_instance().media_path,
            file.filepath
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

        if config_instance().disable_downloading:
            logger.warn(f'Configured to disable real downloading')
        else:
            file.remote_file().download(dest=parent_folderpath)


if __name__ == '__main__':
    logger.warn('Running sync engine in one-off mode')
    SyncEngine().syncnextpendingfile()
