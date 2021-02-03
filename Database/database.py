import logging
from enum import Enum, auto
from functools import total_ordering
from typing import Optional as Opt, List, Dict
import re

import requests
from requests.exceptions import ConnectionError, HTTPError
from bs4 import BeautifulSoup
from pony.orm import Database, PrimaryKey, Required, Optional, Set, commit, db_session

LOGGER = logging.getLogger(__name__)
db = Database()

@total_ordering
class Affinity(Enum):
    PHYSICAL = auto(), 'FF0000'
    MYSTICAL = auto(), '0000FF'
    ENERGY = auto(), '00FF00'

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
    T = auto()

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
    health = Required(int)
    intelligence = Required(int)
    speed = Required(int)
    strength = Required(int)
    order = Optional(str, nullable=True)
    tier = Optional(Tier, nullable=True)
    image_url = Optional(str, nullable=True)

    PrimaryKey(name, title)

    @classmethod
    def safe_insert(cls, name: str, title: str, affinity: Affinity, affiliations: List[Affiliation], health: int, intelligence: int, speed: int, strength: int, order: Opt[str] = None, tier: Opt[Tier] = None, image_url: Opt[str] = None):
        return cls.get(name=name, title=title) or cls(name=name, title=title, affinity=affinity, affiliations=affiliations, health=health, intelligence=intelligence, speed=speed, strength=strength, order=order, tier=tier, image_url=image_url)

    def __lt__(self, other):
        return (self.tier is None, self.tier, self.name, self.title) < (other.tier is None, other.tier, other.name, other.title)


def update_data():
    # region Pull DB data
    html = get_request("/characters")
    soup = BeautifulSoup(html, 'html.parser')
    characters = soup.find_all('div', {'class': ['row parent-row']})
    entries = []
    for character in characters:
        # if "rich-text" not in section.contents[0]:
        LOGGER.debug(character)
        tiers = [*list(Tier), None]
        entry = {
            'Affinity': list(Affinity)[int(character['data-sort-affinity']) - 1],
            'HP': int(character['data-sort-hp']),
            'Intelligence': int(character['data-sort-intel']),
            'Name': character['data-sort-name'].title(),
            'Speed': int(character['data-sort-speed']),
            'Strength': int(character['data-sort-strength']),
            'Tier': tiers[int(character['data-sort-tier'])]
        }
        entry['Title'] = character.contents[1].contents[1].contents[3].contents[3].text
        order_text = character.contents[1].contents[3].contents[11].text
        REGEX = r'.*?(\d{1}).+?(\d{1}).+?(\d{1}).+?(\d{1}).+?(\d{1}).*'
        if match := re.search(REGEX, order_text, re.IGNORECASE):
            entry['Legendary Order'] = ', '.join(match.groups())
        else:
            entry['Legendary Order'] = None
        affiliations = [x.strip().split(', ') for x in character.contents[1].contents[3].contents[27].text.split(' and ') if x]
        temp = []
        for item in affiliations:
            temp.extend(item)
        entry['Affiliations'] = temp

        entries.append(entry)
    # endregion
    for entry in entries:
        affiliations = [Affiliation.safe_insert(x) for x in entry['Affiliations']]
        Character.safe_insert(
            name = entry['Name'],
            title = entry['Title'],
            affinity= entry['Affinity'],
            affiliations=affiliations,
            health = entry['HP'],
            intelligence=entry['Intelligence'],
            speed = entry['Speed'],
            strength = entry['Strength'],
            order = entry['Legendary Order'],
            tier = entry['Tier']
        )

HEADERS = {
    'Content-Type': 'application/json'
}
TIMEOUT = 100
BASE_URL = 'https://dcltoolkit.com'

def get_request(endpoint: str, params: Opt[Dict[str, str]] = None):
    params = params or {}
    url = BASE_URL + endpoint
    try:
        response = requests.get(url=url, headers=HEADERS, timeout=TIMEOUT, params=params)
        LOGGER.debug(f"URL: {response.url}")
        response.raise_for_status()
        LOGGER.info(f"{response.status_code}: GET - {endpoint}")
        return response.text
    except HTTPError as err:
        LOGGER.error(err)
        return []
    except ConnectionError as err:
        LOGGER.critical(f"Unable to access `{url}`")
        return []