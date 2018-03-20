import enum

from sqlalchemy import Column, String, Enum

from ..db import Base


class ConfigType(enum.Enum):
    string = 'str'
    integer = 'int'


class ConfigItem(Base):
    __tablename__ = 'configs'

    name = Column(String, primary_key=True)
    type = Column(Enum(ConfigType), nullable=False)
    value = Column(String)
