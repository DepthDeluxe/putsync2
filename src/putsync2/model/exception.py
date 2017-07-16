from enum import Enum


class PutsyncExceptionType(Enum):
    scan = 0
    download = 1
    configuration = 3
    filesystem = 4
    unknown = 99999


class PutsyncException(Exception):
    def __init__(self, type, description=''):
        self.type = type
        self.description = description

        self.message = self.__get_message()

    def __get_message(self):
        return {
            PutsyncExceptionType.scan: 'Scanning error',
            PutsyncExceptionType.download: 'Download error',
            PutsyncExceptionType.configuration: 'Configuration error',
            PutsyncExceptionType.filesystem: 'Filesystem error',
            PutsyncExceptionType.unknown: 'Unknown error'
        }[self.type]
