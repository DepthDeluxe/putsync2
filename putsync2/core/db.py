from enum import Enum

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .configuration import PutsyncConfig

logger = logging.getLogger(__name__)


Base = declarative_base()
Session = sessionmaker()


class SessionContext(object):
    def __init__(self, autocommit=True):
        logger.debug('Starting new session')
        self._session = Session()
        self._autocommit = autocommit

    def __enter__(self):
        return self._session

    def __exit__(self, type, value, traceback):
        logger.debug('Exiting session')
        if type is None:
            if self._autocommit:
                logger.debug('Since no exception, comitting before close')
                self._session.commit()
        else:
            logger.debug('Hit exception, rolling back session before close')
            self._session.rollback()

        self._session.close()


def init():
    # properly format the relative pathing for db file.  If this isn't done,
    # pony will choose the location of script file as the current directory
    # for some unknown reason
    database_path = PutsyncConfig().database_path
    if database_path[0] != '/':
        database_path = (os.getcwd() + '/' + database_path).replace('/./', '/')

    engine = create_engine(f'sqlite:///{database_path}')
    Session.configure(bind=engine)

    Base.metadata.create_all(engine)
