import os
import logging
from threading import Thread
import time

import putiopy
from pony.orm import db_session, select

from .models.download import Download
from .configuration import PutsyncConfig

logger = logging.getLogger(__name__)


class Scanner(object):
    def __init__(self):
        self.client = putiopy.Client(PutsyncConfig().putio_token)
        self.current_traversed_path = ['']
        self.new_downloads = []

    def scan(self, root_id=0):
        try:
            root_item = self.client.File.get(root_id)
        except Exception:
            logger.exception('Unable to get root file path, stopping scan')
            return

        self.current_traversed_path += self._get_full_path(root_item)

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
        remote_item = self.client.File.get(remote_item.parent_id)
        while remote_item.id != 0:
            logger.debug(f'Current path list: {out}')
            out.insert(0, remote_item.name)
            remote_item = self.client.File.get(remote_item.parent_id)

        logger.debug(f'Final full path: {out}')
        return out

    def _is_folder(self, remote_item):
        return remote_item.file_type == 'FOLDER'

    def _process_folder_or_print_error(self, remote_folder):
        try:
            self._process_folder(remote_folder)
        except Exception as e:
            logger.exception(f'Error scanning folder {remote_folder.name}')

    def _process_folder(self, remote_folder):
        # handle both root level and standard file
        logger.info(f'Processing folder {remote_folder.name}')

        # only add traversed path if we aren't at the root folder
        # root folder has name 'Your Files' which isn't desired
        if remote_folder.id != 0:
            self.current_traversed_path.append(remote_folder.name)

        for remote_item in remote_folder.dir():
            if self._is_folder(remote_item):
                self._process_folder_or_print_error(remote_item)
            else:
                self._process_file_or_print_error(remote_item)

        self.current_traversed_path.pop()

    def _process_file_or_print_error(self, remote_file):
        try:
            self._process_file(remote_file)
        except Exception as e:
            logger.exception(f'Error scanning file {remote_file.name}')

    @db_session
    def _process_file(self, remote_file):
        logger.info(f'Processing file {remote_file.name}, {remote_file.id}')

        # check for existing downloads
        if self._download_exists(remote_file):
            logger.info('File previously scanned')
        else:
            logger.info('This is a new file, adding to system...')
            logger.debug(
                f'Current traversed path: {self.current_traversed_path}'
            )
            Download(
                remote_file_id=remote_file.id,
                filepath=os.path.join(
                    *self.current_traversed_path,
                    remote_file.name
                ),
                size=remote_file.size
            )

    @db_session
    def _download_exists(self, remote_file):
        existing_download = select(
            d for d in Download
            if d.remote_file_id == remote_file.id
        )
        if len(existing_download) > 0:
            return True
        else:
            return False


class ScannerThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        scan_interval = PutsyncConfig().full_scan_interval_minutes

        while True:
            logger.info(f'Sleeping for {scan_interval} minutes before running full scan')
            time.sleep((60*60)*scan_interval)

            Scanner().scan()
