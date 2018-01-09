import os
import logging
from threading import Thread
import time

import putiopy
from pony.orm import db_session, select

from . import filecollection
from .configuration import PutsyncConfig

logger = logging.getLogger(__name__)


class Scanner(object):
    def __init__(self):
        self._client = PutsyncConfig().getclient()
        self._current_traversed_path = ['']

    def scan(self, root_id=0):
        try:
            root_item = self._client.File.get(root_id)
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
        remote_item = self._client.File.get(remote_item.parent_id)
        while remote_item.id != 0:
            logger.debug(f'Current path list: {out}')
            out.insert(0, remote_item.name)
            remote_item = self._client.File.get(remote_item.parent_id)

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

            filecollection.add(
                remote_file=remote_file,
                filepath=filepath
            )
        except Exception as e:
            logger.exception(f'Error scanning file {remote_file.name}')
