import customtkinter as ctk

from meta.compare_advisor import CompareAdvisor
from meta.mana_impact_advisor import ManaImpactAdvisor
from utils.text_shortcuts import bind_text_shortcuts


class MetaPanel(ctk.CTkFrame):
    """
    Панель меты, сравнения и сформированной колоды.

    Внутренние вкладки:
    - Мета;
    - Сравнение;
    - Новая колода.
    """

    META_TAB = "Мета"
    COMPARE_TAB = "Сравнение"
    DECK_TAB = "Новая колода"

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self,
            text="Мета / Compare",
            font=("Arial", 18, "bold"),
        )
        self.title.pack(pady=(10, 5))

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.meta_tab = self.tabs.add(self.META_TAB)
        self.compare_tab = self.tabs.add(self.COMPARE_TAB)
        self.deck_tab = self.tabs.add(self.DECK_TAB)

        self.meta_text = self._create_textbox(self.meta_tab)

        self.compare_text = self._create_textbox(self.compare_tab)

        self.deck_text = self._create_textbox(self.deck_tab)

        self.current_textbox = self.meta_text

        self.tabs.set(self.META_TAB)

    def _create_textbox(self, parent):
        textbox = ctk.CTkTextbox(
            parent,
            width=500,
            height=500,
        )
        textbox.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8,
        )

        bind_text_shortcuts(textbox)

        return textbox

    # ======================================================
    # Meta
    # ======================================================

    def show_snapshot(self, snapshot):
        self._select_output(
            tab_name=self.META_TAB,
            textbox=self.meta_text,
        )

        self._clear_current()

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

    def show_loading(self, format_name):
        self._select_output(
            tab_name=self.META_TAB,
            textbox=self.meta_text,
        )

        self._clear_current()

        self._write("Загрузка меты...\n\n")
        self._write(f"Формат: {format_name}\n")

    # ======================================================
    # Compare
    # ======================================================

    def show_compare_result(
        self,
        comparison,
        user_deck=None,
        reference_deck=None,
    ):
        self._select_output(
            tab_name=self.COMPARE_TAB,
            textbox=self.compare_text,
        )

        self._clear_current()

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

    def show_compare_loading(self):
        self._select_output(
            tab_name=self.COMPARE_TAB,
            textbox=self.compare_text,
        )

        self._clear_current()

        self._write("Сравнение колод...\n\n")
        self._write(
            "Загружаю эталонную колоду с MTGDecks " "и сравниваю её с текущей.\n"
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

        self._write(f"Общее совпадение    : " f"{overall.get('similarity', 0)}%\n")
        self._write(f"Совпадение mainboard: " f"{mainboard.get('similarity', 0)}%\n")
        self._write(f"Совпадение sideboard: " f"{sideboard.get('similarity', 0)}%\n")

        self._write_separator()

        self._write("### MAINBOARD ###\n\n")

        self._write_compare_block(
            comparison=mainboard,
            user_deck_cards=(user_deck.cards if user_deck else None),
            reference_deck_cards=(reference_deck.cards if reference_deck else None),
        )

        self._write_separator()

        self._write("### SIDEBOARD ###\n\n")

        self._write_compare_block(
            comparison=sideboard,
            user_deck_cards=(user_deck.sideboard if user_deck else None),
            reference_deck_cards=(reference_deck.sideboard if reference_deck else None),
        )

        self._write_separator()

        self._write("### ПРОВЕРКА МАНЫ ПОСЛЕ " "MAINBOARD-ЗАМЕН ###\n\n")

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
            if item["ok"]:
                status = "OK"
            else:
                shortage = abs(item["difference"])
                status = f"НЕ ХВАТАЕТ {shortage}"

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
            self._write(f"Твоя колода       : " f"{user_deck.mainboard_size} карт\n")

        if reference_deck is not None:
            self._write(
                f"Эталонная колода  : " f"{reference_deck.mainboard_size} карт\n"
            )

        self._write("\n")

        self._write(f"Совпадение: " f"{comparison.get('similarity', 0)}%\n\n")

        self._write_compare_block(
            comparison=comparison,
            user_deck_cards=(user_deck.cards if user_deck else None),
            reference_deck_cards=(reference_deck.cards if reference_deck else None),
        )

    def _write_compare_block(
        self,
        comparison,
        user_deck_cards=None,
        reference_deck_cards=None,
    ):
        missing_cards = comparison.get(
            "missing_cards",
            {},
        )

        extra_cards = comparison.get(
            "extra_cards",
            {},
        )

        matched_cards = comparison.get(
            "matched_cards",
            {},
        )

        self._write("=== Не хватает ===\n\n")

        if not missing_cards:
            self._write("Недостающих карт нет.\n")
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

    # ======================================================
    # Upgraded deck
    # ======================================================

    def show_upgraded_deck_text(self, deck_text):
        self._select_output(
            tab_name=self.DECK_TAB,
            textbox=self.deck_text,
        )

        self._clear_current()

        self._write("=== Обновлённая колода ===\n\n")

        self._write(deck_text)
        self._write("\n")

    # ======================================================
    # Common
    # ======================================================

    def show_error(self, message):
        self._clear_current()

        self._write("Ошибка\n\n")
        self._write(str(message))

    def clear(self):
        for textbox in (
            self.meta_text,
            self.compare_text,
            self.deck_text,
        ):
            textbox.delete("1.0", "end")

    def _select_output(
        self,
        tab_name,
        textbox,
    ):
        self.tabs.set(tab_name)
        self.current_textbox = textbox

    def _clear_current(self):
        self.current_textbox.delete(
            "1.0",
            "end",
        )

    def _write_separator(self):
        self._write("\n")
        self._write("=" * 50)
        self._write("\n\n")

    def _write(self, text):
        self.current_textbox.insert(
            "end",
            text,
        )
