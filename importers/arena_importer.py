from pathlib import Path

from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry
from parsers.decklist_parser import DecklistParser


class ArenaImporter(BaseImporter):
    """
    Импорт колоды в формате MTG Arena.
    """

    def load(self, source):

        text = self._read_text(source)

        return DecklistParser().parse_text(text)

    def _read_text(self, source):

        source_text = str(source)

        if "\n" in source_text:
            return source_text

        path = Path(source_text)

        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")

        return source_text


registry.register(
    DeckFormat.ARENA,
    ArenaImporter(),
)
