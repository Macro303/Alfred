import logging
from enum import Enum, auto
from functools import total_ordering
from typing import Optional as Opt, List

from pony.orm import Database, PrimaryKey, Required, Optional, Set

LOGGER = logging.getLogger(__name__)
db = Database()

@total_ordering
class Affinity(Enum):
    PHYSICAL = auto(), 'FF0000'
    ENERGY = auto(), '00FF00'
    MYSTICAL = auto(), '0000FF'

    def __new__(cls, value: int, colour_code: str):
        member = object.__new__(cls)
        member._value_ = value
        member.colour_code = colour_code
        return member

    def __str__(self):
        return self.name.title()

    def __lt__(self, other):
        return self.name < other.name

    # def __eq__(self, other):
    #     if isinstance(other, Stat):
    #         return self.value == other.value
    #     return False

    @classmethod
    def find(cls, name: Opt[str]):
        if name:
            for value, entry in cls.__members__.items():
                if name.lower() == value.lower():
                    return entry
        return cls.PHYSICAL


@total_ordering
class Tier(Enum):
    S = auto()
    A = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    F = auto()

    def __str__(self):
        return self.name.title()

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        if isinstance(other, Tier):
            return self.value == other.value
        return False

    @classmethod
    def find(cls, name: Opt[str]):
        if name:
            for value, entry in cls.__members__.items():
                if name.lower() == value.lower():
                    return entry
        return None

@total_ordering
class Affiliation(db.Entity):
    name = PrimaryKey(str)

    # Reverse Columns
    characters = Set('Character')

    @classmethod
    def safe_insert(cls, name: str):
        return cls.get(name=name) or cls(name=name)

    def __lt__(self, other):
        return self.name < other.name

    # def __eq__(self, other):
    #     if isinstance(other, Tag):
    #         return self.name == other.name
    #     return False


class Character(db.Entity):
    name = Required(str)
    title = Required(str)
    affinity = Required(Affinity)
    affiliations = Set(Affiliation)
    tier = Optional(Tier, nullable=True)
    image_url = Optional(str, nullable=True)

    PrimaryKey(name, title)

    @classmethod
    def safe_insert(cls, name: str, title: str, affinity: Affinity, affiliations: List[Affiliation], tier: Opt[Tier] = None, image_url: Opt[str] = None):
        return cls.get(name=name, title=title) or cls(name=name, title=title, affinity=affinity, affiliations=affiliations, tier=tier, image_url=image_url)

    def __lt__(self, other):
        return (self.tier is None, self.tier, self.name, self.title) < (other.tier is None, other.tier, other.name, other.title)

    # def __eq__(self, other):
    #     if isinstance(other, Character):
    #         return self.name == other.name
    #     return False
