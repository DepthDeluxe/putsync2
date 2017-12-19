from configparser import ConfigParser


class ConfigError(Exception):
    def __init__(self, message=None):
        if message is None:
            message = 'General configuration error'
        self.message = message


class Config(object):
    __filepath__ = None
    __parsed_config__ = None

    def __init__(self, section):
        self.section = section

    def get(self, item):
        return self.__parsed_config__.get(self.section, item)

    def getint(self, item):
        return self.__parsed_config__.getint(self.section, item)

    def getboolean(self, item):
        return self.__parsed_config__.getboolean(self.section, item)

    @staticmethod
    def setconfigfilepath(filepath):
        Config.__filepath__ = filepath
        Config.__parsed_config__ = ConfigParser()
        Config.__parsed_config__.read(Config.__filepath__)


class WebappConfig(Config):
    def __init__(self):
        super().__init__('webapp')

        self.dist_path = self.get('dist_path')


class PutsyncConfig(Config):
    def __init__(self):
        super().__init__('putsync')

        self.log_level = self.get('log_level')
        self.putio_token = self.get('putio_token')
        self.database_path = self.get('database_path')
        self.media_path = self.get('media_path')
        self.processor_threads = self.getint('processor_threads')
        self.full_scan_interval_minutes = self.getint('full_scan_interval_minutes')
        self.disable_downloading = self.getboolean('disable_downloading')
