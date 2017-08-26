import os
import shutil
import logging

from pony.orm import db_session, select

from ..core.configuration import getputsyncconfig
from ..core.models.download import Download, DownloadStatus

logger = logging.getLogger(__name__)

@db_session
def purgeinprogressdownloads():
    logger.info('Purging in-progress downloads')

    i = 0
    for download in select(d for d in Download if d.status == DownloadStatus.in_progress.value):
        logger.info(f'Purging {download.filepath}')

        # remove the filepath if they exist
        full_local_media_path = os.path.dirname(os.path.join(getputsyncconfig().media_path, download.filepath))
        try:
            os.remove(full_local_media_path)
        except IsADirectoryError:
            shutil.rmtree(full_local_media_path)
        except FileNotFoundError:
            logger.warn('File not found, continuing')
        
        # purge the downloads
        download.delete()

        i += 1

    logger.info(f'Done purging, purged {i} records')
