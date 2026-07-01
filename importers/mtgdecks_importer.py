from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry
from providers.mtgdecks_provider import MTGDecksProvider


class MTGDecksImporter(BaseImporter):
    """
    Импорт колоды по ссылке MTGDecks.

    Пример:
    https://mtgdecks.net/Pioneer/...
    """

    def load(self, source):

        provider = MTGDecksProvider()

        return provider.get_deck(source)


registry.register(
    DeckFormat.MTGDECKS,
    MTGDecksImporter(),
)
