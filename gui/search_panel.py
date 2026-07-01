import customtkinter as ctk

from utils.text_shortcuts import bind_text_shortcuts


class SearchPanel(ctk.CTkFrame):
    """
    Панель поиска карты.
    """

    def __init__(self, master, callback):
        super().__init__(master)

        self.callback = callback

        self.entry = ctk.CTkEntry(
            self,
            width=400,
            placeholder_text="Введите название карты...",
        )

        self.button = ctk.CTkButton(
            self,
            text="Найти",
            command=self.search,
        )

        self.entry.pack(
            side="left",
            padx=10,
            pady=10,
        )

        self.button.pack(
            side="left",
            padx=10,
        )

        self.entry.bind(
            "<Return>",
            self._on_enter,
        )

        bind_text_shortcuts(self.entry)

    def search(self):
        self.callback(self.entry.get())

    def _on_enter(self, event):
        self.search()

        return "break"
