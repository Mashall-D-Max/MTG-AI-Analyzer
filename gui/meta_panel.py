import customtkinter as ctk

from meta.compare_advisor import CompareAdvisor
from meta.mana_impact_advisor import ManaImpactAdvisor
from utils.text_shortcuts import bind_text_shortcuts


class MetaPanel(ctk.CTkFrame):
    """
    Панель отображения меты и сравнения колод.
    """

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self,
            text="Мета / Compare",
            font=("Arial", 18, "bold"),
        )
        self.title.pack(pady=10)

        self.text = ctk.CTkTextbox(
            self,
            width=360,
            height=500,
        )
        self.text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        bind_text_shortcuts(self.text)

    def show_snapshot(self, snapshot):
        self.text.delete("1.0", "end")

        self._write("=== Meta Snapshot ===\n\n")
        self._write(f"Format : {snapshot.format_name}\n")
        self._write(f"Source : {snapshot.source_name}\n")
        self._write(f"Count  : {snapshot.count}\n\n")

        self._write("=== Top Archetypes ===\n\n")

        if snapshot.count == 0:
            self._write("Архетипы не найдены.\n")
            return

        for archetype in snapshot.top_archetypes(15):
            self._write(f"{archetype.name} | " f"{archetype.meta_share}%")

            if archetype.win_rate:
                self._write(f" | WR {archetype.win_rate}%")

            if archetype.tier:
                self._write(f" | {archetype.tier}")

            self._write("\n")

    def show_compare_result(
        self,
        comparison,
        user_deck=None,
        reference_deck=None,
    ):
        self.text.delete("1.0", "end")

        if "mainboard" in comparison:
            self._show_full_compare_result(
                comparison=comparison,
                user_deck=user_deck,
                reference_deck=reference_deck,
            )
            return

        self._show_single_compare_result(
            title="Mainboard",
            comparison=comparison,
            user_deck=user_deck,
            reference_deck=reference_deck,
        )

    def _show_full_compare_result(
        self,
        comparison,
        user_deck=None,
        reference_deck=None,
    ):
        mainboard = comparison.get("mainboard", {})
        sideboard = comparison.get("sideboard", {})
        overall = comparison.get("overall", {})

        self._write("=== Meta Compare ===\n\n")

        if user_deck is not None:
            self._write(
                f"Твоя колода       : "
                f"{user_deck.mainboard_size} main / "
                f"{user_deck.sideboard_size} side\n"
            )

        if reference_deck is not None:
            self._write(
                f"Эталонная колода  : "
                f"{reference_deck.mainboard_size} main / "
                f"{reference_deck.sideboard_size} side\n"
            )

        self._write("\n")

        self._write(f"Overall similarity  : {overall.get('similarity', 0)}%\n")
        self._write(f"Mainboard similarity: {mainboard.get('similarity', 0)}%\n")
        self._write(f"Sideboard similarity: {sideboard.get('similarity', 0)}%\n")

        self._write("\n")
        self._write("=" * 40)
        self._write("\n\n")

        self._write("### MAINBOARD ###\n\n")

        self._write_compare_block(
            comparison=mainboard,
            user_deck_cards=user_deck.cards if user_deck else None,
            reference_deck_cards=reference_deck.cards if reference_deck else None,
        )

        self._write("\n")
        self._write("=" * 40)
        self._write("\n\n")

        self._write("### SIDEBOARD ###\n\n")

        self._write_compare_block(
            comparison=sideboard,
            user_deck_cards=user_deck.sideboard if user_deck else None,
            reference_deck_cards=reference_deck.sideboard if reference_deck else None,
        )

        self._write("\n")
        self._write("=" * 40)
        self._write("\n\n")

        self._write("### ПРОВЕРКА МАНЫ ПОСЛЕ MAINBOARD-ЗАМЕН ###\n\n")

        if user_deck is None or reference_deck is None:
            self._write("Нет данных для проверки маны.\n")
            return

        mana_report = ManaImpactAdvisor().analyze(
            user_deck=user_deck,
            comparison=mainboard,
            user_deck_cards=user_deck.cards,
            reference_deck_cards=reference_deck.cards,
        )

        if not mana_report:
            self._write("Цветных требований по мане не найдено.\n")
            return

        for item in mana_report:
            status = "OK" if item["ok"] else "НЕ ХВАТАЕТ"

            self._write(
                f"{item['symbol']} {item['name']}: "
                f"источники {item['sources']} / "
                f"требования {item['required']} "
                f"({item['difference']}) — {status}\n"
            )

    def _show_single_compare_result(
        self,
        title,
        comparison,
        user_deck=None,
        reference_deck=None,
    ):
        self._write(f"=== Meta Compare: {title} ===\n\n")

        if user_deck is not None:
            self._write(f"Твоя колода       : {user_deck.mainboard_size} карт\n")

        if reference_deck is not None:
            self._write(f"Эталонная колода  : {reference_deck.mainboard_size} карт\n")

        self._write("\n")
        self._write(f"Совпадение: {comparison.get('similarity', 0)}%\n\n")

        self._write_compare_block(
            comparison=comparison,
            user_deck_cards=user_deck.cards if user_deck else None,
            reference_deck_cards=reference_deck.cards if reference_deck else None,
        )

    def _write_compare_block(
        self,
        comparison,
        user_deck_cards=None,
        reference_deck_cards=None,
    ):
        missing_cards = comparison.get("missing_cards", {})
        extra_cards = comparison.get("extra_cards", {})
        matched_cards = comparison.get("matched_cards", {})

        self._write("=== Не хватает ===\n\n")

        if not missing_cards:
            self._write("Ничего не не хватает.\n")
        else:
            for card_name, quantity in sorted(missing_cards.items()):
                self._write(f"{quantity} {card_name}\n")

        self._write("\n=== Лишние карты ===\n\n")

        if not extra_cards:
            self._write("Лишних карт нет.\n")
        else:
            for card_name, quantity in sorted(extra_cards.items()):
                self._write(f"{quantity} {card_name}\n")

        self._write("\n=== Совпало ===\n\n")

        if not matched_cards:
            self._write("Совпадений нет.\n")
        else:
            for card_name, quantity in sorted(matched_cards.items()):
                self._write(f"{quantity} {card_name}\n")

        self._write("\n=== Рекомендации по заменам ===\n\n")

        recommendations = CompareAdvisor().build_recommendations(
            comparison=comparison,
            user_deck_cards=user_deck_cards,
            reference_deck_cards=reference_deck_cards,
        )

        if not recommendations:
            self._write("Рекомендаций по заменам нет.\n")
            return

        for recommendation in recommendations:
            mana_change = recommendation.get(
                "mana_change",
                "мана: нет данных",
            )

            self._write(
                f"Убрать {recommendation['quantity']} "
                f"{recommendation['remove']} -> "
                f"добавить {recommendation['quantity']} "
                f"{recommendation['add']} | "
                f"{mana_change}\n"
            )

    def show_loading(self, format_name):
        self.text.delete("1.0", "end")

        self._write("Загрузка меты...\n\n")
        self._write(f"Формат: {format_name}\n")

    def show_compare_loading(self):
        self.text.delete("1.0", "end")

        self._write("Сравнение колод...\n\n")
        self._write("Загружаю эталонную колоду с MTGDecks и сравниваю с текущей.\n")

    def show_error(self, message):
        self.text.delete("1.0", "end")

        self._write("Ошибка\n\n")
        self._write(str(message))

    def clear(self):
        self.text.delete("1.0", "end")

    def _write(self, text):
        self.text.insert("end", text)
