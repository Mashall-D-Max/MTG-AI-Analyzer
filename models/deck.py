from models.deck_card import DeckCard


class Deck:
    """
    Модель колоды.

    cards      — mainboard;
    sideboard  — sideboard.

    Поддерживает добавление, изменение количества,
    удаление и перенос карт между зонами.
    """

    MAINBOARD = "mainboard"
    SIDEBOARD = "sideboard"

    def __init__(self):
        self.cards = []
        self.sideboard = []

    # ======================================================
    # Добавление
    # ======================================================

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

    # ======================================================
    # Редактирование по зоне и индексу
    # ======================================================

    def set_quantity(
        self,
        zone,
        index,
        quantity,
    ):
        zone_list = self.get_zone(zone)
        deck_card = self._get_card_by_index(
            zone_list,
            index,
        )

        try:
            normalized = int(quantity)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "Количество должно быть целым числом"
            ) from error

        if normalized < 0:
            raise ValueError(
                "Количество не может быть отрицательным"
            )

        if normalized == 0:
            zone_list.pop(index)
            return None

        deck_card.set_quantity(normalized)
        return deck_card

    def change_quantity(
        self,
        zone,
        index,
        delta,
    ):
        zone_list = self.get_zone(zone)
        deck_card = self._get_card_by_index(
            zone_list,
            index,
        )

        try:
            normalized_delta = int(delta)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "Изменение количества должно быть целым числом"
            ) from error

        new_quantity = (
            deck_card.quantity
            + normalized_delta
        )

        if new_quantity <= 0:
            zone_list.pop(index)
            return None

        deck_card.set_quantity(new_quantity)
        return deck_card

    def remove_at(
        self,
        zone,
        index,
    ):
        zone_list = self.get_zone(zone)
        self._get_card_by_index(
            zone_list,
            index,
        )

        return zone_list.pop(index)

    def move_card(
        self,
        source_zone,
        index,
        target_zone=None,
    ):
        normalized_source = self._normalize_zone_name(
            source_zone
        )

        if target_zone is None:
            normalized_target = (
                self.SIDEBOARD
                if normalized_source == self.MAINBOARD
                else self.MAINBOARD
            )
        else:
            normalized_target = self._normalize_zone_name(
                target_zone
            )

        source_list = self.get_zone(
            normalized_source
        )

        target_list = self.get_zone(
            normalized_target
        )

        deck_card = self._get_card_by_index(
            source_list,
            index,
        )

        if source_list is target_list:
            return deck_card

        source_list.pop(index)

        existing = self._find_matching_deck_card(
            zone=target_list,
            card_name=deck_card.name,
            printing_data=deck_card.printing_data,
        )

        if existing is not None:
            existing.add_quantity(
                deck_card.quantity
            )
            existing.set_printing_data_if_missing(
                deck_card.printing_data
            )
            return existing

        target_list.append(deck_card)
        return deck_card

    def get_zone(self, zone):
        normalized = self._normalize_zone_name(
            zone
        )

        if normalized == self.MAINBOARD:
            return self.cards

        return self.sideboard

    # ======================================================
    # Совместимость со старым API
    # ======================================================

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
        printing_data=None,
    ):
        return self._find_matching_deck_card(
            zone=self.cards,
            card_name=card_name,
            printing_data=printing_data,
        )

    def find_sideboard_card(
        self,
        card_name,
        printing_data=None,
    ):
        return self._find_matching_deck_card(
            zone=self.sideboard,
            card_name=card_name,
            printing_data=printing_data,
        )

    # ======================================================
    # Свойства
    # ======================================================

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

    # ======================================================
    # Внутренние методы
    # ======================================================

    def _add_to_zone(
        self,
        zone,
        card,
        quantity,
        printing_data,
    ):
        card_name = self._card_name(card)

        existing = self._find_matching_deck_card(
            zone=zone,
            card_name=card_name,
            printing_data=printing_data,
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
        existing = self._find_matching_deck_card(
            zone=zone,
            card_name=card_name,
            printing_data=None,
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
    def _find_matching_deck_card(
        zone,
        card_name,
        printing_data,
    ):
        normalized_name = str(
            card_name
        ).strip().casefold()

        if not normalized_name:
            return None

        for deck_card in zone:
            if deck_card.matches(
                card_name=normalized_name,
                printing_data=printing_data,
            ):
                return deck_card

        return None

    @classmethod
    def _normalize_zone_name(cls, zone):
        normalized = str(zone).strip().casefold()

        aliases = {
            "main": cls.MAINBOARD,
            "mainboard": cls.MAINBOARD,
            "deck": cls.MAINBOARD,
            "side": cls.SIDEBOARD,
            "sideboard": cls.SIDEBOARD,
            "sb": cls.SIDEBOARD,
        }

        if normalized not in aliases:
            raise ValueError(
                f"Неизвестная зона колоды: {zone}"
            )

        return aliases[normalized]

    @staticmethod
    def _get_card_by_index(
        zone,
        index,
    ):
        try:
            normalized_index = int(index)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "Индекс карты должен быть целым числом"
            ) from error

        if (
            normalized_index < 0
            or normalized_index >= len(zone)
        ):
            raise IndexError(
                "Карта с таким индексом отсутствует"
            )

        return zone[normalized_index]

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
