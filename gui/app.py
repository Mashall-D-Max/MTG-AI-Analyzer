import customtkinter as ctk

from tkinter import filedialog

from analyzer.deck_analyzer import DeckAnalyzer
from api.scryfall import get_card
from gui.card_panel import CardPanel
from gui.deck_analysis_panel import DeckAnalysisPanel
from gui.deck_list_panel import DeckListPanel
from gui.image_panel import ImagePanel
from gui.meta_panel import MetaPanel
from gui.search_panel import SearchPanel
from gui.status_bar import StatusBar
from importers.import_manager import ImportManager
from providers.mtgdecks_provider import MTGDecksProvider
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
        self.geometry("1800x850")

        self.paste_window = None

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

        self.paste_deck_button = ctk.CTkButton(
            self.top_panel,
            text="Вставить колоду",
            command=self.open_paste_deck_window,
        )
        self.paste_deck_button.pack(side="left", padx=10, pady=10)

        self.load_meta_button = ctk.CTkButton(
            self.top_panel,
            text="Загрузить мету Pioneer",
            command=self.load_pioneer_meta,
        )
        self.load_meta_button.pack(side="left", padx=10, pady=10)

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

        self.deck_list_panel = DeckListPanel(self.center)
        self.deck_list_panel.pack(
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

        self.meta_panel = MetaPanel(self.center)
        self.meta_panel.pack(
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

        self.analyze_deck_source(
            filename,
            success_prefix="Колода загружена из файла.",
        )

    def open_paste_deck_window(self):
        if self.paste_window is not None and self.paste_window.winfo_exists():
            self.paste_window.focus()
            return

        self.paste_window = ctk.CTkToplevel(self)
        self.paste_window.title("Вставить колоду")
        self.paste_window.geometry("700x600")

        title = ctk.CTkLabel(
            self.paste_window,
            text="Вставь decklist",
            font=("Arial", 22, "bold"),
        )
        title.pack(pady=15)

        hint = ctk.CTkLabel(
            self.paste_window,
            text=("Поддерживается обычный список, " "Arena export и Sideboard."),
        )
        hint.pack(pady=(0, 10))

        self.paste_textbox = ctk.CTkTextbox(
            self.paste_window,
            width=650,
            height=400,
        )
        self.paste_textbox.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10,
        )

        buttons_panel = ctk.CTkFrame(self.paste_window)
        buttons_panel.pack(fill="x", padx=20, pady=15)

        analyze_button = ctk.CTkButton(
            buttons_panel,
            text="Анализировать",
            command=self.analyze_pasted_deck,
        )
        analyze_button.pack(side="left", padx=10)

        close_button = ctk.CTkButton(
            buttons_panel,
            text="Закрыть",
            command=self.paste_window.destroy,
        )
        close_button.pack(side="left", padx=10)

        example_button = ctk.CTkButton(
            buttons_panel,
            text="Вставить пример",
            command=self.insert_example_deck,
        )
        example_button.pack(side="left", padx=10)

    def insert_example_deck(self):
        example = """Deck
4 Fatal Push (MKM) 84
4 Thoughtseize (AKR) 127
4 Ketramose, the New Dawn (DFT) 17
2 Plains (DMU) 277
2 Swamp (DMU) 279

Sideboard
2 Duress (M21) 96
"""

        self.paste_textbox.delete("1.0", "end")
        self.paste_textbox.insert("1.0", example)

    def analyze_pasted_deck(self):
        deck_text = self.paste_textbox.get("1.0", "end").strip()

        if not deck_text:
            self.status.label.configure(text="Вставленный decklist пустой")
            return

        self.analyze_deck_source(
            deck_text,
            success_prefix="Колода загружена из текста.",
        )

        if self.paste_window is not None and self.paste_window.winfo_exists():
            self.paste_window.destroy()

    def analyze_deck_source(self, source, success_prefix):
        self.status.label.configure(text="Загрузка и анализ колоды...")

        try:
            deck = ImportManager().load(source)

            analysis = DeckAnalyzer(deck).analyze()

            self.deck_list_panel.show_deck(deck)
            self.deck_analysis_panel.show_analysis(analysis)

            self.status.label.configure(
                text=(
                    f"{success_prefix} "
                    f"Mainboard: {deck.mainboard_size}, "
                    f"Sideboard: {deck.sideboard_size}"
                )
            )

        except Exception as error:
            self.deck_list_panel.show_error(str(error))
            self.deck_analysis_panel.show_error(str(error))

            self.status.label.configure(text="Ошибка загрузки колоды")

    def load_pioneer_meta(self):
        format_name = "Pioneer"

        self.meta_panel.show_loading(format_name)

        self.status.label.configure(text="Загрузка меты Pioneer...")

        try:
            provider = MTGDecksProvider()

            snapshot = provider.get_meta(format_name)

            self.meta_panel.show_snapshot(snapshot)

            self.status.label.configure(
                text=(f"Мета Pioneer загружена. " f"Архетипов: {snapshot.count}")
            )

        except Exception as error:
            self.meta_panel.show_error(str(error))

            self.status.label.configure(text="Ошибка загрузки меты")
