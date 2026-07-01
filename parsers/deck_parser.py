from pathlib import Path

from parsers.decklist_parser import DecklistParser


def load_deck(filename):
    """
    Загрузить колоду из текстового файла.

    Старый интерфейс сохранён для совместимости.
    """

    path = Path(filename)

    text = path.read_text(encoding="utf-8")

    return DecklistParser().parse_text(text)
