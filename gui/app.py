import customtkinter as ctk

from tkinter import filedialog

from analyzer.deck_analyzer import DeckAnalyzer
from api.scryfall import get_card
from gui.card_panel import CardPanel
from gui.deck_analysis_panel import DeckAnalysisPanel
from gui.image_panel import ImagePanel
from gui.search_panel import SearchPanel
from gui.status_bar import StatusBar
from importers.import_manager import ImportManager
from services.image_service import load_card_image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """
    Главное окно приложения.
    """

    def __init__(self):
        super().__init__()

        self.title("MTG AI Analyzer")
        self.geometry("1400x800")

        self.title_label = ctk.CTkLabel(
            self,
            text="MTG AI Analyzer",
            font=("Arial", 30, "bold"),
        )
        self.title_label.pack(pady=15)

        self.top_panel = ctk.CTkFrame(self)
        self.top_panel.pack(fill="x", padx=20)

        self.search_panel = SearchPanel(
            self.top_panel,
            self.search_card,
        )
        self.search_panel.pack(side="left", padx=10, pady=10)

        self.open_deck_button = ctk.CTkButton(
            self.top_panel,
            text="Открыть колоду",
            command=self.open_deck_file,
        )
        self.open_deck_button.pack(side="left", padx=10, pady=10)

        self.center = ctk.CTkFrame(self)
        self.center.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        self.image_panel = ImagePanel(self.center)
        self.image_panel.pack(
            side="left",
            fill="y",
            padx=10,
        )

        self.card_panel = CardPanel(self.center)
        self.card_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
        )

        self.deck_analysis_panel = DeckAnalysisPanel(self.center)
        self.deck_analysis_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
        )

        self.status = StatusBar(self)
        self.status.pack(
            fill="x",
            side="bottom",
        )

    def search_card(self, card_name):
        card_name = card_name.strip()

        if not card_name:
            self.status.label.configure(text="Введите название карты")
            return

        self.status.label.configure(text=f"Загрузка карты: {card_name}")

        card = get_card(card_name)

        if card is None:
            self.status.label.configure(text="Карта не найдена")
            return

        self.card_panel.show_card(card)

        image = load_card_image(card)

        self.image_panel.show_image(image)

        self.status.label.configure(text=f"Загружена карта: {card.name}")

    def open_deck_file(self):
        filename = filedialog.askopenfilename(
            title="Открыть колоду",
            filetypes=[
                ("Deck files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if not filename:
            return

        self.status.label.configure(text=f"Загрузка колоды: {filename}")

        try:
            deck = ImportManager().load(filename)

            analysis = DeckAnalyzer(deck).analyze()

            self.deck_analysis_panel.show_analysis(analysis)

            self.status.label.configure(
                text=(
                    "Колода загружена. "
                    f"Mainboard: {deck.mainboard_size}, "
                    f"Sideboard: {deck.sideboard_size}"
                )
            )

        except Exception as error:
            self.deck_analysis_panel.show_error(str(error))

            self.status.label.configure(text="Ошибка загрузки колоды")
