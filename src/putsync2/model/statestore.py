import os

from putsync2.model.configuration import getputsyncconfig
import putsync2.model.util as util
from putsync2.model.exception import PutsyncException, PutsyncExceptionType


def commit(download):
    config = getputsyncconfig()

    try:
        full_local_metadata_path = os.path.join(config.metadata_path, download.path)
        util.mkdir_p(full_local_metadata_path)
        open(f'{full_local_metadata_path}/{download.remote_file.name}.done', 'a').close()
    except OSError as os_error:
        raise PutsyncException(PutsyncExceptionType.filesystem, description=os_error)


def isprocessed(download):
    config = getputsyncconfig()

    try:
        full_local_metadata_path = os.path.join(config.metadata_path, download.path)
        return os.path.isfile(f'{full_local_metadata_path}/{download.remote_file.name}.done')
    except OSError as os_error:
        raise PutsyncException(PutsyncExceptionType.filesystem, description=os_error)
