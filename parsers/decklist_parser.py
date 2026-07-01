import re

from api.scryfall import get_card
from models.deck import Deck
from utils.logger import logger


class DecklistParser:
    """
    Универсальный парсер текстовых decklist-форматов.

    Поддерживает:

    4 Fatal Push
    4 Thoughtseize

    Deck
    4 Fatal Push (MKM) 84

    Sideboard
    2 Duress (M21) 96
    """

    ARENA_SET_PATTERN = re.compile(r"\s+\([A-Z0-9]{2,6}\)\s+\S+\s*$")

    PRICE_PATTERN = re.compile(
        r"\s+[$€]\s*\d+|\s+\d+(?:[.,]\d+)?\s*tix",
        re.IGNORECASE,
    )

    GARBAGE_MARKERS = (
        "$",
        "€",
        " tix",
        "@cardhoarder",
        "@tcgplayer",
        "@cardkingdom",
        "hover a card",
        "report deck error",
        "last update",
        "add/remove",
        "collection quantity",
        "visual view",
        "list view",
        "copy to clipboard",
    )

    def parse_text(self, text):
        deck = Deck()

        lines = str(text).splitlines()

        in_sideboard = False

        for line in lines:
            line = line.strip().lstrip("\ufeff")

            if not line:
                continue

            if line.startswith("#"):
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
                logger.warning(f"Карта пропущена, Scryfall не нашёл: {card_name}")
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

        if not self._is_valid_card_name(card_name):
            logger.warning(f"Пропущена подозрительная строка decklist: {line}")
            return None

        return quantity, card_name

    def _clean_card_name(self, card_name):
        card_name = str(card_name).strip()

        card_name = self.ARENA_SET_PATTERN.sub("", card_name)

        card_name = self.PRICE_PATTERN.split(card_name, maxsplit=1)[0]

        lower_name = card_name.lower()

        for marker in self.GARBAGE_MARKERS:
            index = lower_name.find(marker)

            if index != -1:
                card_name = card_name[:index]
                lower_name = card_name.lower()

        card_name = re.sub(
            r"\s+[CURM]\s*$",
            "",
            card_name,
        )

        return " ".join(card_name.split()).strip()

    def _is_valid_card_name(self, card_name):
        if not card_name:
            return False

        if len(card_name) > 90:
            return False

        if card_name.isdigit():
            return False

        if not any(char.isalpha() for char in card_name):
            return False

        lower_name = card_name.lower()

        for marker in self.GARBAGE_MARKERS:
            if marker in lower_name:
                return False

        bad_values = {
            "deck",
            "sideboard",
            "maindeck",
            "image",
            "visual view",
            "list view",
            "copy to clipboard",
            "quantity",
            "collection",
        }

        if lower_name in bad_values:
            return False

        return True
