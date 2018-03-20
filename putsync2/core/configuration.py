from configparser import ConfigParser
import os

import putiopy


m_singleton_filepath = None


class ConfigError(Exception):
    def __init__(self, message=None):
        if message is None:
            message = 'General configuration error'
        self.message = message


class ConfigFile(object):
    __filepath__ = None
    __parsed_config__ = None

    def __init__(self, filepath, section='putsync'):
        self._filepath = filepath
        self._config = ConfigParser()
        self._config.read(self._filepath)
        self._section = section

        self.dist_path = self._config.get(self._section, 'dist_path')
        self.log_level = self._config.get(self._section, 'log_level')
        self.putio_token = self._config.get(self._section, 'putio_token')
        self.database_path = self._config.get(self._section, 'database_path')
        self.media_path = self._config.get(self._section, 'media_path')
        self.processor_threads = self._config.getint(self._section, 'processor_threads')
        self.full_scan_interval_minutes = self._config.getint(self._section, 'full_scan_interval_minutes')
        self.disable_downloading = self._config.getboolean(self._section, 'disable_downloading')

    def getclient(self):
        return putiopy.Client(
            self.putio_token
        )

    def absolutedistpath(self):
        return os.path.abspath(self.dist_path)


def config_instance():
    return ConfigFile(m_singleton_filepath)


def set_config_filepath(filepath):
    global m_singleton_filepath

    m_singleton_filepath = filepath
