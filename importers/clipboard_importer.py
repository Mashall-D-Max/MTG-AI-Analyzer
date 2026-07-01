import re

from api.scryfall import get_card
from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry
from models.deck import Deck


class ClipboardImporter(BaseImporter):
    """
    Импорт колоды из вставленного текста.

    Поддерживает формат:

    4 Fatal Push
    4 Thoughtseize
    2 Plains

    Sideboard
    2 Duress
    """

    ARENA_SET_PATTERN = re.compile(r"\s+\([A-Z0-9]{2,6}\)\s+\S+\s*$")

    def load(self, source):

        deck = Deck()

        lines = str(source).splitlines()

        in_sideboard = False

        for line in lines:

            line = line.strip().lstrip("\ufeff")

            if not line:
                continue

            lower_line = line.lower()

            if lower_line == "deck":
                in_sideboard = False
                continue

            if lower_line == "sideboard":
                in_sideboard = True
                continue

            parsed = self._parse_card_line(line)

            if parsed is None:
                continue

            quantity, card_name = parsed

            card = get_card(card_name)

            if card is None:
                continue

            if in_sideboard:
                deck.add_sideboard_card(card, quantity)
            else:
                deck.add_card(card, quantity)

        return deck

    def _parse_card_line(self, line):

        parts = line.split(" ", 1)

        if len(parts) != 2:
            return None

        quantity_text, card_name = parts

        try:
            quantity = int(quantity_text)
        except ValueError:
            return None

        card_name = self._clean_card_name(card_name)

        if not card_name:
            return None

        return quantity, card_name

    def _clean_card_name(self, card_name):

        card_name = card_name.strip()

        card_name = self.ARENA_SET_PATTERN.sub("", card_name)

        return card_name.strip()


registry.register(
    DeckFormat.CLIPBOARD,
    ClipboardImporter(),
)
