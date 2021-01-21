import logging

from pony.orm import db_session

from Database import Availability, Tier, Character
from Logger import init_logger

LOGGER = logging.getLogger(__name__)


def main():
    with db_session:
        Availability.select().show(width=175)
        Tier.select().show(width=175)
        Character.select().show(width=175)


if __name__ == "__main__":
    init_logger('Alfred_Database')
    main()
