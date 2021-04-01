import logging

from pony.orm import db_session

import PyLogger
from Database import Affiliation, Character

LOGGER = logging.getLogger(__name__)


def main():
    with db_session:
        Affiliation.select().show(width=175)
        Character.select().show(width=175)


if __name__ == "__main__":
    PyLogger.init('Alfred_Database')
    main()
