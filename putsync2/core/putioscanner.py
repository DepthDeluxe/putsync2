import os
import logging

import putiopy
from pony import orm

from .models.download import Download
from .configuration import getputsyncconfig
from ..util.synchronization import locked

logger = logging.getLogger(__name__)

client = None
current_traversed_path = None
new_downloads = []

@locked
@orm.db_session
def scan(root_id=0):
    global current_traversed_path

    # initialize the scanner before using it each time
    __init()

    root_item = client.File.get(root_id)
    current_traversed_path += __get_full_path(root_item)

    if __is_folder(root_item):
        __process_folder_or_print_error(root_item)
    else:
        __process_file_or_print_error(root_item)


def __init():
    global client, current_traversed_path, new_downloads

    client = client or putiopy.Client(getputsyncconfig().putio_token)
    current_traversed_path = ['']
    newdownloads = []


def __get_full_path(remote_item):
    out = []

    # return early if the root item is actually the root folder
    if remote_item.id == 0:
        return out

    # keep looping while id is not zero, this will skip top folder
    # so it is not included in the name convention
    remote_item = client.File.get(remote_item.parent_id)
    while remote_item.id != 0:
        out.insert(0, remote_item)
        remote_item = client.File.get(remote_item.parent_id)

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
    global new_downloads

    logger.info('Processing file %s', remote_file.name)

    # check for existing downloads
    if __download_exists(remote_file):
        logger.info('File previously scanned')
    else:
        logger.info('This is a new file, adding to system...')
        new_downloads.append(
            Download(
                remote_file_id=remote_file.id,
                filepath=os.path.join(*current_traversed_path, remote_file.name),
                size=remote_file.size
            )
        )


def __download_exists(remote_file):
    existing_download = orm.select(d for d in Download if d.remote_file_id == remote_file.id)
    if len(existing_download) > 0:
        return True
    else:
        return False

