import logging
import threading

from pony import orm

from ..core.configuration import getputsyncconfig
from ..core.models.download import DownloadStatus
from ..util.synchronization import locked

logger = logging.getLogger(__name__)

@orm.db_session
def processdownload(download):
    config = getputsyncconfig()

    if not __checkdownloadvalidandmarkinprogress(download):
        return

    # get the remote file and disable file verification because it is slow
    remote_file = putiopy.Client(config.putio_token).File.get(download.remote_file_id)
    __disable_file_verification(remote_file)

    logger.info(f'Starting download of {remote_file.name}')

    full_local_media_path = os.path.dirname(os.path.join(config.media_path, self.filepath))
    os.makedirs(full_local_media_path)

    if config.disable_downloading:
        logger.warn(f'Not actually downloading {remote_file.name}, configured to disable real downloading')
    else:
        remote_file.download(dest=full_local_media_path)

    download.markdone()
    logger.info(f'{remote_file.name} download successful')


@locked
def __checkdownloadvalidandmarkinprogress(download):
    if download.status != DownloadStatus.new.value:
        logger.warn(f'Attempting to download {download.remote_file_id} when in {download.status} state, skipping')
        return False
    else:
        download.markinprogress()
        return True


def __disable_file_verification(self, remote_file):
    def __new_verify_file(*args, **kwargs):
        return True

    remote_file._verify_file = __new_verify_file
    logger.info('File verification disabled')
