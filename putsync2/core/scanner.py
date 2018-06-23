import os
import logging

from ..db import SessionContext
from .file import FileCollection
from .task import Task
from .putio import PutioClient

logger = logging.getLogger(__name__)


class Scanner(object):
    def __init__(self, putio_token, name='scanner'):
        self._putio_client = PutioClient(putio_token)
        self._current_traversed_path = ['']

        self._task = Task(name)

    def scan(self, root_id=0):
        self._task.running()

        try:
            self._scan(root_id)
        finally:
            self._task.idle()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._task.close()

    def _scan(self, root_id):
        try:
            root_item = self._putio_client.fetch_remote_file(root_id)
        except Exception:
            logger.exception('Unable to get root file path, stopping scan')
            return

        self._current_traversed_path += self._get_full_path(root_item)

        if self._is_folder(root_item):
            self._process_folder_or_print_error(root_item)
        else:
            self._process_file_or_print_error(root_item)

    def _get_full_path(self, remote_item):
        logger.debug('Building full path')
        out = []

        # return early if the root item is actually the root folder
        if remote_item.id == 0:
            return out

        # keep looping while id is not zero, this will skip top folder
        # so it is not included in the name convention
        remote_item = self._putio_client.fetch_remote_file(
            remote_item.parent_id)
        while remote_item.id != 0:
            logger.debug(f'Current path list: {out}')
            out.insert(0, remote_item.name)
            remote_item = self._putio_client.fetch_remote_file(
                remote_item.parent_id)

        logger.debug(f'Final full path: {out}')
        return out

    def _is_folder(self, remote_item):
        return remote_item.file_type == 'FOLDER'

    def _process_folder_or_print_error(self, remote_folder):
        try:
            # handle both root level and standard file
            logger.info(f'Processing folder {remote_folder.name}')

            # only add traversed path if we aren't at the root folder
            # root folder has name 'Your Files' which isn't desired
            if remote_folder.id != 0:
                self._current_traversed_path.append(remote_folder.name)

            for remote_item in remote_folder.dir():
                if self._is_folder(remote_item):
                    self._process_folder_or_print_error(remote_item)
                else:
                    self._process_file_or_print_error(remote_item)

            self._current_traversed_path.pop()
        except Exception as e:
            logger.exception(f'Error scanning folder {remote_folder.name}')

    def _process_file_or_print_error(self, remote_file):
        try:
            logger.info(
                f'Processing file {remote_file.name}, {remote_file.id}'
            )

            # check for existing downloads
            logger.info('This is a new file, adding to system...')
            logger.debug(
                f'Current traversed path: {self._current_traversed_path}'
            )

            filepath = os.path.join(
                *self._current_traversed_path,
                remote_file.name
            )

            with SessionContext() as session:
                FileCollection(session).add(
                    remote_file=remote_file,
                    filepath=filepath
                )
        except Exception as e:
            logger.exception(f'Error scanning file {remote_file.name}')
