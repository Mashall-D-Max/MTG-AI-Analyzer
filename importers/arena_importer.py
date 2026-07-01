import re
from pathlib import Path

from api.scryfall import get_card
from importers.base_importer import BaseImporter
from importers.deck_format import DeckFormat
from importers.registry import registry
from models.deck import Deck


class ArenaImporter(BaseImporter):
    """
    Импорт колоды в формате MTG Arena.

    Поддерживает строки вида:

    Deck
    4 Fatal Push (MKM) 84
    2 Plains (DMU) 277

    Sideboard
    2 Duress (M21) 96

    На текущем этапе Sideboard игнорируется.
    """

    ARENA_SET_PATTERN = re.compile(r"\s+\([A-Z0-9]{2,6}\)\s+\S+\s*$")

    def load(self, source):

        deck = Deck()

        lines = self._read_lines(source)

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

            if in_sideboard:
                continue

            parsed = self._parse_card_line(line)

            if parsed is None:
                continue

            quantity, card_name = parsed

            card = get_card(card_name)

            if card is None:
                continue

            deck.add_card(card, quantity)

        return deck

    def _read_lines(self, source):

        source_text = str(source)

        if "\n" in source_text:
            return source_text.splitlines()

        path = Path(source_text)

        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8").splitlines()

        return source_text.splitlines()

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
    DeckFormat.ARENA,
    ArenaImporter(),
)
