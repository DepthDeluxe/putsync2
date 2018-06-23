from configparser import ConfigParser


class ConfigurationManager(object):
    def __init__(self, filepath):
        self._filepath = filepath
        self._config = None

    def get(self):
        if self._config is None:
            self._config = Configuration.load(self._filepath)

        return self._config

    def expire(self):
        self._config = None


class Configuration(object):
    def __init__(self, config):
        self.system = SystemConfiguration(config)
        self.webapp = WebappConfiguration(config)
        self.backend = BackendConfiguration(config)

    @classmethod
    def load(cls, filepath):
        config = ConfigParser()
        config.read(filepath)

        return cls(config)


class SystemConfiguration(object):
    section = 'system'

    def __init__(self, config):
        self.log_level = config.get(self.section, 'log_level')


class WebappConfiguration(object):
    section = 'webapp'

    def __init__(self, config):
        self.dist_path = config.get(self.section, 'dist_path')


class BackendConfiguration(object):
    section = 'backend'

    def __init__(self, config):
        self.database_path = config.get(
            self.section, 'database_path')
        self.media_path = config.get(
            self.section, 'media_path')
        self.processor_threads = int(config.get(
            self.section, 'processor_threads'))
        self.full_scan_interval_minutes = int(config.get(
            self.section, 'full_scan_interval_minutes'))
        self.disable_downloading = bool(config.get(
            self.section, 'disable_downloading'))
        self.putio_token = config.get(
            self.section, 'putio_token')
