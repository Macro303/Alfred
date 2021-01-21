import logging
from typing import Optional as Opt

from pony.orm import Database, PrimaryKey, Required, Set, Optional

LOGGER = logging.getLogger(__name__)
db = Database()


class Availability(db.Entity):
    name = PrimaryKey(str)
    colour_code = Required(str, default='000000', sql_default='000000')

    # Reflective Columns
    characters = Set('Character')

    @classmethod
    def safe_insert(cls, name: str, colour_code: str = '000000'):
        return cls.get(name=name) or cls(name=name, colour_code=colour_code)


class Tier(db.Entity):
    index = PrimaryKey(int)
    name = Required(str, unique=True)

    # Reflective Columns
    characters = Set('Character')

    @classmethod
    def safe_insert(cls, index: int, name: str):
        return cls.get(index=index, name=name) or cls(index=index, name=name)


class Character(db.Entity):
    name = PrimaryKey(str)
    availability = Optional(Availability, nullable=True)
    tier = Optional(Tier, nullable=True)
    image_url = Optional(str, nullable=True)

    @classmethod
    def safe_insert(cls, name: str, tier: Opt[Tier] = None, availability: Opt[Availability] = None, image_url: Opt[str] = None):
        return cls.get(name=name) or cls(name=name, tier=tier, availability=availability, image_url=image_url)
