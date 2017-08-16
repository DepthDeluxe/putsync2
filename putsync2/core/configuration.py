import configparser


class ServerConfig(object):
    def __init__(self, config):
        self.host = config.get('server', 'host')
        self.port = config.getint('server', 'port')
        self.dist_path = config.get('server', 'dist_path')


class PutsyncConfig(object):
    def __init__(self, config):
        self.putio_token = config.get('putsync', 'putio_token')
        self.database_path = config.get('putsync', 'database_path')
        self.media_path = config.get('putsync', 'media_path')
        self.download_threads = config.getint('putsync', 'download_threads')
        self.full_scan_interval_minutes = config.getint('putsync', 'full_scan_interval_minutes')
        self.disable_downloading = config.getboolean('putsync', 'disable_downloading')


parsedconfig = None


def setconfigfilepath(filepath):
    global parsedconfig

    parsedconfig = configparser.ConfigParser()
    parsedconfig.read(filepath)


def getserverconfig():
    return ServerConfig(parsedconfig)


def getputsyncconfig():
    return PutsyncConfig(parsedconfig)
