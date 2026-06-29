from services.image_service import load_card_image
from api.scryfall import get_card
import customtkinter as ctk

from gui.search_panel import SearchPanel
from gui.card_panel import CardPanel
from gui.image_panel import ImagePanel
from gui.status_bar import StatusBar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("MTG AI Analyzer")
        self.geometry("1200x750")

        # Заголовок
        self.title_label = ctk.CTkLabel(
            self, text="MTG AI Analyzer", font=("Arial", 30, "bold")
        )

        self.title_label.pack(pady=20)

        # Поиск
        self.search_panel = SearchPanel(self, self.search_card)
        self.search_panel.pack()

        # Центральная область
        self.center = ctk.CTkFrame(self)
        self.center.pack(fill="both", expand=True, padx=20, pady=20)

        # Левая панель
        self.image_panel = ImagePanel(self.center)
        self.image_panel.pack(side="left", fill="y", padx=10)

        # Правая панель
        self.card_panel = CardPanel(self.center)
        self.card_panel.pack(side="left", fill="both", expand=True)

        # Строка состояния
        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

    def search_card(self, card_name):

        card_name = card_name.strip()

        if not card_name:
            self.status.label.configure(text="Введите название карты")
            return

        card = get_card(card_name)
        print("IMAGE_URIS:")
        print(card.image_uris)
        print("=" * 50)
        print("IMAGE URIS")
        print(card.image_uris)
        print("=" * 50)

        if card:
            self.card_panel.show_card(card)
            image = load_card_image(card)

            print("image =", image)
            print("type =", type(image))

            self.image_panel.show_image(image)
            self.status.label.configure(text=f"Загружена карта: {card.name}")
        else:
            self.status.label.configure(text="Карта не найдена")
