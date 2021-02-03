import logging
from enum import Enum
from pathlib import Path

from Database.database import db, Affinity, Affiliation, Tier, Character, update_data
from Database.enum_converter import EnumConverter

TOP_DIR = Path(__file__).resolve().parent.parent
LOGGER = logging.getLogger(__name__)

db.bind(
    provider='sqlite',
    filename=str(TOP_DIR.joinpath('Alfred.sqlite')),
    create_db=True
)
db.provider.converter_classes.append((Enum, EnumConverter))
db.generate_mapping(create_tables=True)


@db.on_connect(provider='sqlite')
def sqlite_case_sensitivity(database, connection):
    cursor = connection.cursor()
    cursor.execute('PRAGMA case_sensitive_like = OFF')
