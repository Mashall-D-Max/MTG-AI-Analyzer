from enum import Enum


class DeckFormat(Enum):
    """
    Поддерживаемые форматы импорта колод.
    """

    TXT = "txt"
    ARENA = "arena"
    MOXFIELD = "moxfield"
    ARCHIDEKT = "archidekt"
    MTGDECKS = "mtgdecks"
    URL = "url"
    CLIPBOARD = "clipboard"
