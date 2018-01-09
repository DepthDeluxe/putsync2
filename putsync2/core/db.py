import logging
import os

from pony import orm

from .configuration import PutsyncConfig

logger = logging.getLogger(__name__)


# set to none on initialization as it relies on config which is
# initialized in main()
db = orm.Database()


class PutsyncEntity(db.Entity):
    @orm.db_session
    @classmethod
    def clean(cls):
        cls.delete()


def init():
    logger.info('Initializing database, creating tables as necessary')

    # properly format the relative pathing for db file.  If this isn't done,
    # pony will choose the location of script file as the current directory
    # for some unknown reason
    database_path = PutsyncConfig().database_path
    if database_path[0] != '/':
        database_path = os.getcwd() + '/' + database_path

    db.bind(provider='sqlite', filename=database_path, create_db=True)
    db.generate_mapping(create_tables=True)
    orm.set_sql_debug(True)
