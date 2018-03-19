from enum import Enum

import logging
import os

from pony.orm import db_session, Database
from pony.orm.dbapiprovider import StrConverter

from .configuration import PutsyncConfig

logger = logging.getLogger(__name__)


# set to none on initialization as it relies on config which is
# initialized in main()
db = Database()


class PutsyncEntity(db.Entity):
    @db_session
    @classmethod
    def clean(cls):
        cls.delete()


class EnumConverter(StrConverter):
    def validate(self, val, obj):
        if not isinstance(val, Enum):
            raise ValueError(f'Type must be enum, got {type(val)}')

        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, value):
        return self.py_type[value]


def init():
    logger.info('Initializing database, creating tables as necessary')

    # properly format the relative pathing for db file.  If this isn't done,
    # pony will choose the location of script file as the current directory
    # for some unknown reason
    database_path = PutsyncConfig().database_path
    if database_path[0] != '/':
        database_path = os.getcwd() + '/' + database_path

    db.bind(provider='sqlite', filename=database_path, create_db=True)
    db.provider.converter_classes.append((Enum, EnumConverter))
    db.generate_mapping(create_tables=True)
