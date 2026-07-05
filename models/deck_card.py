class DeckCard:
    """
    Одна строка колоды.

    card          — модель карты приложения;
    quantity      — количество копий;
    printing_data — исходный JSON выбранного издания Scryfall.
    """

    def __init__(
        self,
        card,
        quantity,
        printing_data=None,
    ):
        if card is None:
            raise ValueError("Карта не указана")

        self.card = card
        self.quantity = self._normalize_quantity(quantity)
        self.printing_data = self._copy_printing_data(
            printing_data
        )

    @property
    def name(self):
        return str(
            getattr(self.card, "name", "")
        ).strip()

    @property
    def normalized_name(self):
        return self.name.casefold()

    @property
    def set_code(self):
        if not self.printing_data:
            return ""

        return str(
            self.printing_data.get("set", "")
        ).upper().strip()

    @property
    def collector_number(self):
        if not self.printing_data:
            return ""

        return str(
            self.printing_data.get(
                "collector_number",
                "",
            )
        ).strip()

    @property
    def language(self):
        if not self.printing_data:
            return ""

        return str(
            self.printing_data.get("lang", "")
        ).strip()

    @property
    def printing_id(self):
        if not self.printing_data:
            return ""

        return str(
            self.printing_data.get("id", "")
        ).strip()

    @property
    def printing_key(self):
        """
        Идентификатор конкретного издания.

        Когда точные данные издания отсутствуют,
        возвращается пустая строка. Это позволяет
        объединять обычные импортированные строки
        с картами того же названия.
        """

        if self.printing_id:
            return f"id:{self.printing_id.casefold()}"

        parts = [
            self.set_code.casefold(),
            self.collector_number.casefold(),
            self.language.casefold(),
        ]

        if any(parts):
            return "printing:" + "|".join(parts)

        return ""

    @property
    def printing_label(self):
        parts = []

        if self.set_code:
            parts.append(self.set_code)

        if self.collector_number:
            parts.append(f"№ {self.collector_number}")

        if self.language:
            parts.append(self.language)

        if not parts:
            return ""

        return "[" + " · ".join(parts) + "]"

    def add_quantity(self, quantity):
        self.quantity += self._normalize_quantity(
            quantity
        )

        return self.quantity

    def remove_quantity(self, quantity):
        quantity = self._normalize_quantity(
            quantity
        )

        self.quantity = max(
            0,
            self.quantity - quantity,
        )

        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = self._normalize_quantity(
            quantity
        )

        return self.quantity

    def set_printing_data_if_missing(
        self,
        printing_data,
    ):
        if self.printing_data:
            return

        self.printing_data = (
            self._copy_printing_data(
                printing_data
            )
        )

    def matches(
        self,
        card_name,
        printing_data=None,
    ):
        normalized_name = str(
            card_name
        ).strip().casefold()

        if self.normalized_name != normalized_name:
            return False

        incoming_key = self._printing_key_from_data(
            printing_data
        )

        current_key = self.printing_key

        # Если хотя бы у одной строки нет точных данных,
        # считаем совпадением карту с тем же названием.
        if not incoming_key or not current_key:
            return True

        return incoming_key == current_key

    @classmethod
    def _printing_key_from_data(
        cls,
        printing_data,
    ):
        if not printing_data:
            return ""

        if not isinstance(printing_data, dict):
            raise TypeError(
                "Данные издания должны быть словарём"
            )

        printing_id = str(
            printing_data.get("id", "")
        ).strip()

        if printing_id:
            return f"id:{printing_id.casefold()}"

        set_code = str(
            printing_data.get("set", "")
        ).strip().casefold()

        collector_number = str(
            printing_data.get(
                "collector_number",
                "",
            )
        ).strip().casefold()

        language = str(
            printing_data.get("lang", "")
        ).strip().casefold()

        parts = [
            set_code,
            collector_number,
            language,
        ]

        if any(parts):
            return "printing:" + "|".join(parts)

        return ""

    @staticmethod
    def _normalize_quantity(quantity):
        try:
            normalized = int(quantity)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "Количество должно быть целым числом"
            ) from error

        if normalized <= 0:
            raise ValueError(
                "Количество должно быть больше нуля"
            )

        return normalized

    @staticmethod
    def _copy_printing_data(printing_data):
        if printing_data is None:
            return None

        if not isinstance(printing_data, dict):
            raise TypeError(
                "Данные издания должны быть словарём"
            )

        return dict(printing_data)
