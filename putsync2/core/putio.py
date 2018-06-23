import putiopy
import logging


logger = logging.getLogger(__name__)


def create_client(putio_token):
    return putiopy.Client(putio_token)


class PutioClient(object):
    def __init__(self, token):
        self._client = putiopy.Client(token)

    def fetch_remote_file(self, remote_id):
        # we want to disable file verification becuase it takes a very long
        # time to run on a Raspberry Pi.  We want to maximize the download
        # rate.
        def _new_verify_file(*args, **kwargs):
            logger.info('File verification called, running stub instead')
            return True

        remote_file = self._client.File.get(remote_id)
        remote_file._verify_file = _new_verify_file

        return remote_file
