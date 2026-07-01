from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry
from parsers.decklist_parser import DecklistParser


class ClipboardImporter(BaseImporter):
    """
    Импорт колоды из вставленного текста.
    """

    def load(self, source):

        return DecklistParser().parse_text(source)


registry.register(
    DeckFormat.CLIPBOARD,
    ClipboardImporter(),
)
