import logging
import os

from putiopy import ClientError

from ..db import SessionContext
from ..util.synchronization import locked

from .task import Task
from .file import File, FileStatus
from .putio import PutioClient

logger = logging.getLogger(__name__)


class Engine(object):
    def __init__(self, putio_token, media_path, disable_downloading=False,
                 name='anonymous-engine'):
        self._putio_client = PutioClient(putio_token)
        self._media_path = media_path
        self._disable_downloading = disable_downloading

        self._task = Task(name)

    def run(self):
        self._task.running()

        try:
            while True:
                next_id = fetch_next_pending_file_id()
                if next_id is None:
                    break

                self._sync(next_id)
        finally:
            self._task.idle()

    def _sync(self, id_):
        with SessionContext() as session:
            file = session.query(File).get(id_)

            try:
                self._attempt(file)
                file.done()
            except Exception as e:
                logger.exception(f'Exception {e} fired when processing file '
                                 f'{file.filepath}')
                file.fail()

            return file.id

    def _attempt(self, file):
        full_filepath = os.path.join(
            self._media_path,
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

        if self._disable_downloading:
            logger.warn(f'Configured to disable real downloading')
        else:
            try:
                remote_file = self._putio_client.fetch_remote_file(
                    file.remote_id)
                remote_file.download(dest=parent_folderpath)
            except ClientError as e:
                if e.type == 'NotFound':
                    logger.error('File not found, will mark as done')
                else:
                    raise e


@locked
def fetch_next_pending_file_id():
    '''
    This fetches the next file_id that is in "pending" state

    This method MUST be locked becuase we are using sqlite
    which has poor concurrency management.  I have found that
    the code hits race conditions when this method isn't locked.
    Also: this is outside of the class because we want a global
    lock on all pending file fetches.
    '''
    with SessionContext() as session:
        file = session.query(File)\
            .filter_by(status=FileStatus.new)\
            .first()

        if file is None:
            return None

        logger.info(f'Processing file {file.id}')
        file.start()

        id_ = file.id

    return id_
