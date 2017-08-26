import logging
import threading
import os

from pony.orm import commit, db_session, select

import putiopy

from ..core.configuration import getputsyncconfig
from ..core.models.download import Download, DownloadStatus
from ..util.synchronization import locked

logger = logging.getLogger(__name__)


def processdownload(id):
    if not checkdownloadvalidandmarkinprogress(id):
        return

    # get the remote file and disable file verification because it is slow
    remote_file = putiopy.Client(getputsyncconfig().putio_token).File.get(id)
    __disable_file_verification(remote_file)

    logger.info(f'Starting download of {remote_file.name}')

    with db_session:
        full_local_media_path = os.path.dirname(os.path.join(getputsyncconfig().media_path, Download[id].filepath))
        try:
            os.makedirs(full_local_media_path)
        except FileExistsError:
            logger.info(f'Folder {full_local_media_path} already exists')
            pass

    if getputsyncconfig().disable_downloading:
        logger.warn(f'Not actually downloading {remote_file.name}, configured to disable real downloading')
    else:
        remote_file.download(dest=full_local_media_path)
   
    # commit the results
    with db_session:
        Download[id].markdone()
    logger.info(f'{remote_file.name} download successful')


@locked
@db_session
def checkdownloadvalidandmarkinprogress(id):
    download = Download[id]

    if download.status != DownloadStatus.new.value:
        logger.debug(f'Attempting to download {download.remote_file_id} when in {download.status} state, skipping')
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
        return select(d for d in Download if d.status == DownloadStatus.new.value).first().remote_file_id
    except AttributeError:
        return None
