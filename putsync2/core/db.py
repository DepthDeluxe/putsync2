from enum import Enum
import logging

from pony import orm
from pony.orm.dbapiprovider import StrConverter


logger = logging.getLogger(__name__)

db = orm.Database(provider='sqlite', filename='./putsync.sqlite3', create_db=True)

class EnumConverter(StrConverter):
    def validate(self, val):
        if not isinstance(val, Enum):
            raise ValueError(f'Must be an enum, type is {type(val)}')
        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, val):
        return self.py_type[val]

    def val2dbval(self, val):
        return val.name

    def dbval2val(self, val):
        return self.py_type[val]


# add the provider to database
db.provider.converter_classes.append((Enum, EnumConverter))

def init():
    logger.info('Initializing database, creating tables as necessary')

    db.generate_mapping(create_tables=True)
