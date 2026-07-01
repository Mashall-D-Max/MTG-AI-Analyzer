import customtkinter as ctk

from utils.mana_symbols import format_mana_cost
from utils.text_shortcuts import bind_text_shortcuts


class CardPanel(ctk.CTkFrame):

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
        )

        self.title.pack(pady=(10, 5))
        self.textbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        # Подключаем горячие клавиши
        bind_text_shortcuts(self.textbox)

    def show_card(self, card):
        self.textbox.delete("1.0", "end")

        mana_cost = format_mana_cost(card.mana_cost)

        text = f"""Название: {card.name}

Стоимость: {mana_cost}
Тип: {card.type_line}
Редкость: {card.rarity}
Сет: {card.set_name}

Oracle Text
------------------------------

{card.oracle_text}
"""

        self.textbox.insert("1.0", text)
