from api.scryfall import get_card
from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry
from models.deck import Deck


class TxtImporter(BaseImporter):
    """
    Импорт обычного TXT-файла.

    Формат строк:

    4 Fatal Push
    2 Plains
    """

    def load(self, filename):

        deck = Deck()

        with open(filename, encoding="utf-8") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                parts = line.split(" ", 1)

                if len(parts) != 2:
                    continue

                quantity_text, card_name = parts

                try:
                    quantity = int(quantity_text)
                except ValueError:
                    continue

                card = get_card(card_name)

                if card is None:
                    continue

                deck.add_card(card, quantity)

        return deck


registry.register(
    DeckFormat.TXT,
    TxtImporter(),
)
