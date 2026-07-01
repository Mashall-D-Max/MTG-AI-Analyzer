from pathlib import Path

from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry
from parsers.decklist_parser import DecklistParser


class TxtImporter(BaseImporter):
    """
    Импорт обычного TXT-файла.
    """

    def load(self, filename):

        text = Path(filename).read_text(encoding="utf-8")

        return DecklistParser().parse_text(text)


registry.register(
    DeckFormat.TXT,
    TxtImporter(),
)
