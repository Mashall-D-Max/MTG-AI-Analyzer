import customtkinter as ctk


class CardPanel(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self, text="Информация о карте", font=("Arial", 22, "bold")
        )

        self.textbox = ctk.CTkTextbox(self, width=500, height=500)

        self.title.pack(pady=(10, 5))
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

    def show_card(self, card):

        self.textbox.delete("1.0", "end")

        text = f"""Название: {card.name}

Стоимость: {card.mana_cost}
Тип: {card.type_line}
Редкость: {card.rarity}
Сет: {card.set_name}

Oracle Text
------------------------------

{card.oracle_text}
"""

        self.textbox.insert("1.0", text)
