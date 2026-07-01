from api.scryfall import get_card
from models.deck import Deck

from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry


class TxtImporter(BaseImporter):
    """
    Импорт обычного TXT-файла.
    """

    def load(self, filename):

        deck = Deck()

        with open(filename, encoding="utf-8") as file:

            for line in file:

                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split(" ", 1)

                if len(parts) != 2:
                    continue

                quantity = int(parts[0])

                card_name = parts[1]

                card = get_card(card_name)

                if card:

                    deck.add_card(card, quantity)

        return deck


registry.register(
    DeckFormat.TXT,
    TxtImporter(),
)
