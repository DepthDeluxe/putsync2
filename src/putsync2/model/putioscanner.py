import os
import logging

from putsync2.model.download import Download
import putsync2.model.statestore as statestore

logger = logging.getLogger(__name__)


class PutioScanner(object):
    def __init__(self, root_id, queue, queue_lock):
        self.root_id = root_id
        self.root_item = None
        self.queue = queue
        self.queue_lock = queue_lock

        # needs to have empty string because os.path.join()
        # requires arguments and *[] is equivalent to sending
        # no arguments
        self.current_traversed_path = ['']

    def run(self, client):
        self.root_item = client.File.get(self.root_id)
        self.current_traversed_path += self.__get_full_path(client)

        if self.__is_folder(self.root_item):
            self.__process_folder_or_print_error(self.root_item)
        else:
            self.__process_file_or_print_error(self.root_item)

    def __get_full_path(self, client):
        current_item = self.root_item
        out = []

        # return early if the root item is actually the root folder
        if current_item.id == 0:
            return out

        # keep looping while id is not zero, this will skip top folder
        # so it is not included in the name convention
        current_item = client.File.get(current_item.parent_id)
        while current_item.id != 0:
            out.insert(0, current_item)
            current_item = client.File.get(current_item.parent_id)

        return out

    def __is_folder(self, remote_item):
        return remote_item.file_type == 'FOLDER'

    def __process_folder_or_print_error(self, remote_folder):
        try:
            self.__process_folder(remote_folder)
        except Exception as e:
            logger.exception('Error scanning folder {remote_folder.name}')

    def __process_folder(self, remote_folder):
        # handle both root level and standard file
        logger.info(f'Processing folder {remote_folder.name}')

        # only add traversed path if we aren't at the root folder
        # root folder has name 'Your Files' which isn't desired
        if remote_folder.id != 0:
            self.current_traversed_path.append(remote_folder.name)

        for remote_item in remote_folder.dir():
            if self.__is_folder(remote_item):
                self.__process_folder_or_print_error(remote_item)
            else:
                self.__process_file_or_print_error(remote_item)

        self.current_traversed_path.pop()

    def __process_file_or_print_error(self, remote_file):
        try:
            self.__process_file(remote_file)
        except Exception as e:
            logger.exception(f'Error scanning file {remote_file.name}')

    def __process_file(self, remote_file):
        logger.info('Processing file %s', remote_file.name)

        download = Download(
            remote_file,
            os.path.join(*self.current_traversed_path)
        )

        # critical section
        self.queue_lock.acquire()
        try:
            if not statestore.isprocessed(download) and download not in self.queue:
                logger.info('File has not been downloaded, adding to queue')
                self.queue.append(download)
            else:
                logger.info('File already processed')
        except Exception as e:
            raise e
        finally:
            self.queue_lock.release()
