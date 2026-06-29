import customtkinter as ctk


class SearchPanel(ctk.CTkFrame):

    def __init__(self, master, callback):
        super().__init__(master)

        self.entry = ctk.CTkEntry(
            self, width=400, placeholder_text="Введите название карты..."
        )

        self.button = ctk.CTkButton(
            self, text="Найти", command=lambda: callback(self.entry.get())
        )

        self.entry.pack(side="left", padx=10, pady=10)
        self.button.pack(side="left", padx=10)

        # Поиск по Enter
        self.entry.bind("<Return>", lambda event: callback(self.entry.get()))
