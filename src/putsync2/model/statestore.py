import os
from threading import Lock

from putsync2.model.configuration import getputsyncconfig
from putsync2.model.exception import PutsyncException, PutsyncExceptionType
from putsync2.util import mkdir_p


lock = Lock()

def commit(download):
    global lock

    config = getputsyncconfig()
    lock.acquire()

    try:
        full_local_metadata_path = os.path.join(config.metadata_path, download.path)
        mkdir_p(full_local_metadata_path)
        open(f'{full_local_metadata_path}/{download.remote_file.name}.done', 'a').close()
    except OSError as os_error:
        raise PutsyncException(PutsyncExceptionType.filesystem, description=os_error)
    finally:
        lock.release()


def isprocessed(download):
    global lock

    config = getputsyncconfig()
    lock.acquire()

    try:
        full_local_metadata_path = os.path.join(config.metadata_path, download.path)
        return os.path.isfile(f'{full_local_metadata_path}/{download.remote_file.name}.done')
    except OSError as os_error:
        raise PutsyncException(PutsyncExceptionType.filesystem, description=os_error)
    finally:
        lock.release()
