import os
import logging
from threading import Lock

import putiopy

from .model.download import Download
from .model.configuration import getputsyncconfig
from .model import statestore

logger = logging.getLogger(__name__)

client = None
current_item = None
current_traversed_path = None
queue = []
queue_lock = Lock()
scan_lock = Lock()

# needs to have empty string because os.path.join()
# requires arguments and *[] is equivalent to sending
# no arguments
current_traversed_path = None


def getqueueandlock():
    return queue, queue_lock


def scan(root_id=0):
    global root_item, current_traversed_path, scan_lock, client

    # initialize the scanner before using it
    __init()

    logger.info('Waiting for scan lock')
    scan_lock.acquire()
    logger.info('Scan lock acquired')
    try:
        root_item = client.File.get(root_id)
        current_traversed_path += __get_full_path(root_item)

        if __is_folder(root_item):
            __process_folder_or_print_error(root_item)
        else:
            __process_file_or_print_error(root_item)
    finally:
        scan_lock.release()
        logger.info('Scan lock released')


def __init():
    global client, current_traversed_path

    client = client or putiopy.Client(getputsyncconfig().putio_token)
    current_traversed_path = ['']


def __get_full_path(remote_item):
    global current_item, client

    current_item = remote_item
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


def __is_folder(remote_item):
    return remote_item.file_type == 'FOLDER'


def __process_folder_or_print_error(remote_folder):
    try:
        __process_folder(remote_folder)
    except Exception as e:
        logger.exception('Error scanning folder {remote_folder.name}')


def __process_folder(remote_folder):
    global current_traversed_path

    # handle both root level and standard file
    logger.info(f'Processing folder {remote_folder.name}')

    # only add traversed path if we aren't at the root folder
    # root folder has name 'Your Files' which isn't desired
    if remote_folder.id != 0:
        current_traversed_path.append(remote_folder.name)

    for remote_item in remote_folder.dir():
        if __is_folder(remote_item):
            __process_folder_or_print_error(remote_item)
        else:
            __process_file_or_print_error(remote_item)

    current_traversed_path.pop()


def __process_file_or_print_error(remote_file):
    try:
        __process_file(remote_file)
    except Exception as e:
        logger.exception(f'Error scanning file {remote_file.name}')


def __process_file(remote_file):
    global current_traversed_path, queue_lock, queue

    logger.info('Processing file %s', remote_file.name)

    download = Download(
        remote_file,
        os.path.join(*current_traversed_path)
    )

    # critical section
    queue_lock.acquire()
    try:
        if not statestore.isprocessed(download) and download not in queue:
            logger.info('File has not been downloaded, adding to queue')
            queue.append(download)
        else:
            logger.info('File already processed')
    finally:
        queue_lock.release()
