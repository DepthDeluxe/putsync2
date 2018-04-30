from enum import Enum


class PutsyncException(Exception):
    def __init__(self, message):
        self.message = message


class ScanPutsyncException(Exception):
    def __init__(self, file_id):
        self.message = f'Error scanning putsync item {file_id}'


class DownloadPutsyncException(Exception):
    def __init__(self, putsync_id, filepath):
        self.message = f'Error downloading file {putsync_id} to destination {filepath}'


class RemoteFileMissingException(Exception):
    def __init__(self, name, remote_id):
        self.message = f'File {remote_id}, name {name} is missing from the remote server'
