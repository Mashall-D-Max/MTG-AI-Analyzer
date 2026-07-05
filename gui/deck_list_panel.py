import customtkinter as ctk

from utils.text_shortcuts import bind_text_shortcuts


class DeckListPanel(ctk.CTkFrame):
    """
    Панель отображения mainboard и sideboard.

    Для карт, добавленных из поиска Scryfall,
    дополнительно показывает точное издание.
    """

    def __init__(self, master):
        super().__init__(master)

        self.current_deck = None

        self.title = ctk.CTkLabel(
            self,
            text="Список колоды",
            font=("Arial", 18, "bold"),
        )
        self.title.pack(
            pady=(10, 4)
        )

        self.summary_label = ctk.CTkLabel(
            self,
            text=(
                "Mainboard: 0 | "
                "Sideboard: 0 | "
                "Всего: 0"
            ),
        )
        self.summary_label.pack(
            pady=(0, 6)
        )

        self.text = ctk.CTkTextbox(
            self,
            width=360,
            height=500,
            wrap="word",
        )
        self.text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10),
        )

        bind_text_shortcuts(self.text)

        self.text.configure(
            state="disabled"
        )

    def show_deck(self, deck):
        self.current_deck = deck

        self.title.configure(
            text="Список колоды"
        )

        self.summary_label.configure(
            text=(
                f"Mainboard: {deck.mainboard_size} | "
                f"Sideboard: {deck.sideboard_size} | "
                f"Всего: {deck.total_size}"
            )
        )

        self._begin_update()

        self._write("=== Mainboard ===\n\n")

        if deck.mainboard_size == 0:
            self._write("Mainboard пуст\n")
        else:
            for deck_card in deck.cards:
                self._write_deck_card(
                    deck_card
                )

        self._write("\n=== Sideboard ===\n\n")

        if deck.sideboard_size == 0:
            self._write("Sideboard пуст\n")
        else:
            for deck_card in deck.sideboard:
                self._write_deck_card(
                    deck_card
                )

        self._end_update()

    def show_error(self, message):
        self.current_deck = None

        self.title.configure(
            text="Список колоды"
        )

        self.summary_label.configure(
            text="Ошибка загрузки"
        )

        self._begin_update()
        self._write(
            "Ошибка загрузки колоды\n\n"
        )
        self._write(str(message))
        self._end_update()

    def clear(self):
        self.current_deck = None

        self.summary_label.configure(
            text=(
                "Mainboard: 0 | "
                "Sideboard: 0 | "
                "Всего: 0"
            )
        )

        self._begin_update()
        self._end_update()

    def _write_deck_card(
        self,
        deck_card,
    ):
        card_name = str(
            getattr(
                deck_card.card,
                "name",
                "Без названия",
            )
        )

        line = (
            f"{deck_card.quantity} "
            f"{card_name}"
        )

        printing_label = str(
            getattr(
                deck_card,
                "printing_label",
                "",
            )
        ).strip()

        if printing_label:
            line += f" {printing_label}"

        self._write(line + "\n")

    def _begin_update(self):
        self.text.configure(
            state="normal"
        )
        self.text.delete(
            "1.0",
            "end",
        )

    def _end_update(self):
        self.text.configure(
            state="disabled"
        )

    def _write(self, text):
        self.text.insert(
            "end",
            text,
        )
