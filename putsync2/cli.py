import click
import logging

from .configuration import ConfigurationManager
from .webapp import app
from .db import setup_database

from .util.offline import OfflineProcessor

logger = logging.getLogger(__name__)


@click.command()
@click.option('--config', required=True, help='Config file location')
def main(config):
    manager = ConfigurationManager(config)
    setup_logging(manager.get().system)
    setup_backend(manager.get().backend)

    app.config['PUTSYNC_CONFIGURATION_MANAGER'] = manager
    app.run()


def setup_logging(config):
    log_level = config.log_level

    loggerformat = '%(asctime)-15s [%(levelname)-8s] : %(name)-20s : '\
                   '%(thread)d : %(message)s'
    logging.basicConfig(format=loggerformat, level=log_level)
    logging.warn(f'Log level set to {log_level}')


def setup_backend(config):
    setup_database(config.database_path)

    logger.info('Initializing the offline processing component')
    offline_processor = OfflineProcessor(config.processor_threads,
                                         config.putio_token, config.media_path,
                                         config.disable_downloading,
                                         config.full_scan_interval_minutes)
    offline_processor.start()


if __name__ == '__main__':
    main()
