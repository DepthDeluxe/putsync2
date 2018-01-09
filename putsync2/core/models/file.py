import logging

from pony.orm import PrimaryKey, Required, Set
import putiopy

from ..db import PutsyncEntity
from .syncattempt import SyncAttempt
from ..configuration import PutsyncConfig

logger = logging.getLogger(__name__)


class File(PutsyncEntity):
    remote_file_id = Required(int, size=64)
    filepath = Required(str)
    size = Required(int, size=64)
    attempts = Set(SyncAttempt)

    def doneat(self):
        pass

    def move(self, new_filepath):
        pass

    def synced(self):
        pass

    def status(self):
        pass

    def markforretry(self):
        pass

    def remotefile(self):
        # we want to disable file verification becuase it takes a very long
        # time to run on a Raspberry Pi.  We want to maximize the download
        # rate.
        def _new_verify_file(*args, **kwargs):
            logger.info('File verification called, running stub instead')
            return True

        remote_file = PutsyncConfig().getclient().File.get(
            self.remote_file_id
        )
        remote_file._verify_file = _new_verify_file

        return remote_file
