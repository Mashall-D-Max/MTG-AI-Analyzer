import customtkinter as ctk

from utils.mana_symbols import format_mana_cost
from utils.text_shortcuts import bind_text_shortcuts


class CardPanel(ctk.CTkFrame):
    """
    Панель информации о карте.

    Поддерживает:
    - старую модель Card приложения;
    - исходный JSON конкретного издания Scryfall.
    """

    LEGALITY_NAMES = {
        "standard": "Standard",
        "pioneer": "Pioneer",
        "explorer": "Explorer",
        "modern": "Modern",
        "legacy": "Legacy",
        "pauper": "Pauper",
        "vintage": "Vintage",
        "commander": "Commander",
        "brawl": "Brawl",
        "standardbrawl": "Standard Brawl",
        "alchemy": "Alchemy",
        "historic": "Historic",
        "timeless": "Timeless",
    }

    LEGALITY_STATUSES = {
        "legal": "легальна",
        "banned": "запрещена",
        "restricted": "ограничена",
        "not_legal": "нелегальна",
    }

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self,
            text="Информация о карте",
            font=("Arial", 22, "bold"),
        )

        self.textbox = ctk.CTkTextbox(
            self,
            width=500,
            height=500,
            wrap="word",
        )

        self.title.pack(pady=(10, 5))
        self.textbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        bind_text_shortcuts(self.textbox)

    def show_loading(self):
        self._set_text("Загрузка информации о карте...")

    def show_error(self, message):
        self._set_text(
            "Не удалось загрузить карту.\n\n"
            f"{message}"
        )

    def show_card(self, card):
        if isinstance(card, dict):
            text = self._build_scryfall_card_text(card)
        else:
            text = self._build_model_card_text(card)

        self._set_text(text)

    def _build_model_card_text(self, card):
        mana_cost = format_mana_cost(
            getattr(card, "mana_cost", "")
        )

        name = getattr(card, "name", "Без названия")
        type_line = getattr(card, "type_line", "")
        rarity = getattr(card, "rarity", "")
        set_name = getattr(card, "set_name", "")
        oracle_text = getattr(card, "oracle_text", "")

        return f"""Название: {name}

Стоимость: {mana_cost}
Тип: {type_line}
Редкость: {rarity}
Сет: {set_name}

Oracle Text
------------------------------

{oracle_text}
"""

    def _build_scryfall_card_text(self, card):
        lines = []

        name = self._clean(card.get("name")) or "Без названия"
        lines.append(f"Название: {name}")

        mana_cost = self._clean(card.get("mana_cost"))
        type_line = self._clean(card.get("type_line"))
        oracle_text = self._clean(card.get("oracle_text"))

        card_faces = card.get("card_faces", [])

        if isinstance(card_faces, list) and card_faces:
            for face in card_faces:
                if not isinstance(face, dict):
                    continue

                face_name = self._clean(face.get("name"))
                face_mana = self._clean(face.get("mana_cost"))
                face_type = self._clean(face.get("type_line"))
                face_oracle = self._clean(face.get("oracle_text"))

                lines.append("")
                lines.append(
                    f"Сторона: {face_name or 'Без названия'}"
                )

                if face_mana:
                    lines.append(
                        "Стоимость: "
                        + format_mana_cost(face_mana)
                    )

                if face_type:
                    lines.append(f"Тип: {face_type}")

                if face_oracle:
                    lines.append("")
                    lines.append("Oracle Text")
                    lines.append("------------------------------")
                    lines.append(face_oracle)

                self._append_stats(lines, face)
        else:
            if mana_cost:
                lines.append(
                    "Стоимость: "
                    + format_mana_cost(mana_cost)
                )

            if type_line:
                lines.append(f"Тип: {type_line}")

            self._append_stats(lines, card)

            if oracle_text:
                lines.append("")
                lines.append("Oracle Text")
                lines.append("------------------------------")
                lines.append(oracle_text)

        set_name = self._clean(card.get("set_name"))
        set_code = self._clean(card.get("set")).upper()
        collector_number = self._clean(
            card.get("collector_number")
        )
        rarity = self._clean(card.get("rarity"))
        language = self._clean(card.get("lang"))
        released_at = self._clean(card.get("released_at"))
        artist = self._clean(card.get("artist"))

        lines.append("")
        lines.append("Издание")
        lines.append("------------------------------")

        if set_name:
            lines.append(f"Набор: {set_name}")

        if set_code:
            lines.append(f"Код набора: {set_code}")

        if collector_number:
            lines.append(
                f"Номер коллекционера: {collector_number}"
            )

        if rarity:
            lines.append(f"Редкость: {rarity.capitalize()}")

        if language:
            lines.append(f"Язык: {language}")

        if released_at:
            lines.append(f"Дата выпуска: {released_at}")

        if artist:
            lines.append(f"Художник: {artist}")

        self._append_prices(
            lines,
            card.get("prices"),
        )

        self._append_legalities(
            lines,
            card.get("legalities"),
        )

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _append_stats(lines, card):
        power = card.get("power")
        toughness = card.get("toughness")
        loyalty = card.get("loyalty")
        defense = card.get("defense")

        if power is not None and toughness is not None:
            lines.append(
                f"Сила / выносливость: {power} / {toughness}"
            )

        if loyalty is not None:
            lines.append(f"Лояльность: {loyalty}")

        if defense is not None:
            lines.append(f"Защита: {defense}")

    def _append_prices(self, lines, prices):
        if not isinstance(prices, dict):
            return

        labels = {
            "usd": "USD",
            "usd_foil": "USD foil",
            "usd_etched": "USD etched",
            "eur": "EUR",
            "eur_foil": "EUR foil",
            "tix": "MTGO TIX",
        }

        visible_prices = []

        for key, label in labels.items():
            value = self._clean(prices.get(key))

            if value:
                visible_prices.append(f"{label}: {value}")

        if not visible_prices:
            return

        lines.append("")
        lines.append("Цены")
        lines.append("------------------------------")
        lines.extend(visible_prices)

    def _append_legalities(self, lines, legalities):
        if not isinstance(legalities, dict):
            return

        visible = []

        for format_name, status in legalities.items():
            if status == "not_legal":
                continue

            visible_name = self.LEGALITY_NAMES.get(
                format_name,
                format_name.replace("_", " ").title(),
            )

            visible_status = self.LEGALITY_STATUSES.get(
                status,
                status,
            )

            visible.append(
                f"{visible_name}: {visible_status}"
            )

        if not visible:
            return

        lines.append("")
        lines.append("Легальность")
        lines.append("------------------------------")
        lines.extend(visible)

    def _set_text(self, text):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.textbox.configure(state="disabled")

    @staticmethod
    def _clean(value):
        if value is None:
            return ""

        return str(value).strip()
