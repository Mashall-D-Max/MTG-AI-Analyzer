from models.deck_card import DeckCard


class Deck:
    """
    Модель колоды.

    cards      — mainboard;
    sideboard  — sideboard.

    При повторном добавлении карта с тем же названием
    объединяется с уже существующей строкой выбранной зоны.
    """

    def __init__(self):
        self.cards = []
        self.sideboard = []

    def add_card(
        self,
        card,
        quantity=1,
        printing_data=None,
    ):
        return self._add_to_zone(
            zone=self.cards,
            card=card,
            quantity=quantity,
            printing_data=printing_data,
        )

    def add_sideboard_card(
        self,
        card,
        quantity=1,
        printing_data=None,
    ):
        return self._add_to_zone(
            zone=self.sideboard,
            card=card,
            quantity=quantity,
            printing_data=printing_data,
        )

    def remove_card(
        self,
        card_name,
        quantity=1,
    ):
        return self._remove_from_zone(
            zone=self.cards,
            card_name=card_name,
            quantity=quantity,
        )

    def remove_sideboard_card(
        self,
        card_name,
        quantity=1,
    ):
        return self._remove_from_zone(
            zone=self.sideboard,
            card_name=card_name,
            quantity=quantity,
        )

    def find_card(
        self,
        card_name,
    ):
        return self._find_in_zone(
            self.cards,
            card_name,
        )

    def find_sideboard_card(
        self,
        card_name,
    ):
        return self._find_in_zone(
            self.sideboard,
            card_name,
        )

    @property
    def size(self):
        return sum(
            deck_card.quantity
            for deck_card in self.cards
        )

    @property
    def mainboard_size(self):
        return self.size

    @property
    def sideboard_size(self):
        return sum(
            deck_card.quantity
            for deck_card in self.sideboard
        )

    @property
    def total_size(self):
        return (
            self.mainboard_size
            + self.sideboard_size
        )

    @property
    def unique_cards(self):
        return len(self.cards)

    @property
    def unique_sideboard_cards(self):
        return len(self.sideboard)

    @property
    def all_cards(self):
        return self.cards + self.sideboard

    def _add_to_zone(
        self,
        zone,
        card,
        quantity,
        printing_data,
    ):
        card_name = self._card_name(card)

        existing = self._find_in_zone(
            zone,
            card_name,
        )

        if existing is not None:
            existing.add_quantity(quantity)
            existing.set_printing_data_if_missing(
                printing_data
            )

            return existing

        deck_card = DeckCard(
            card=card,
            quantity=quantity,
            printing_data=printing_data,
        )

        zone.append(deck_card)

        return deck_card

    def _remove_from_zone(
        self,
        zone,
        card_name,
        quantity,
    ):
        existing = self._find_in_zone(
            zone,
            card_name,
        )

        if existing is None:
            return False

        remaining = existing.remove_quantity(
            quantity
        )

        if remaining == 0:
            zone.remove(existing)

        return True

    @staticmethod
    def _find_in_zone(
        zone,
        card_name,
    ):
        normalized_name = str(
            card_name
        ).strip().casefold()

        if not normalized_name:
            return None

        for deck_card in zone:
            if (
                deck_card.normalized_name
                == normalized_name
            ):
                return deck_card

        return None

    @staticmethod
    def _card_name(card):
        card_name = str(
            getattr(card, "name", "")
        ).strip()

        if not card_name:
            raise ValueError(
                "У карты отсутствует название"
            )

        return card_name
