import customtkinter as ctk
from utils.text_shortcuts import bind_text_shortcuts
from utils.text_shortcuts import bind_text_shortcuts


class DeckListPanel(ctk.CTkFrame):
    """
    Панель отображения списка колоды:
    mainboard и sideboard.
    """

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self,
            text="Список колоды",
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

        # Подключаем горячие клавиши
        bind_text_shortcuts(self.text)

    def show_deck(self, deck):
        self.text.delete("1.0", "end")

        self._write("=== Mainboard ===\n\n")

        for deck_card in deck.cards:
            self._write(f"{deck_card.quantity} {deck_card.card.name}\n")

        self._write("\n=== Sideboard ===\n\n")

        if deck.sideboard_size == 0:
            self._write("Sideboard пуст\n")
            return

        for deck_card in deck.sideboard:
            self._write(f"{deck_card.quantity} {deck_card.card.name}\n")

    def show_error(self, message):
        self.text.delete("1.0", "end")

        self._write("Ошибка загрузки колоды\n\n")
        self._write(message)

    def clear(self):
        self.text.delete("1.0", "end")

    def _write(self, text):
        self.text.insert("end", text)
