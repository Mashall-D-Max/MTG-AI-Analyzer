from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry


class ArenaImporter(BaseImporter):
    """
    Импорт колоды в формате MTG Arena.

    Пока заглушка. Реализация будет в следующем этапе.
    """

    def load(self, source):

        raise NotImplementedError("Arena Importer пока не реализован.")


registry.register(
    DeckFormat.ARENA,
    ArenaImporter(),
)
