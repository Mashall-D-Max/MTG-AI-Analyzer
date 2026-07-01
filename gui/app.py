import threading

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
from meta.meta_compare import MetaCompare
from providers.mtgdecks_provider import MTGDecksProvider
from services.image_service import load_card_image
from utils.text_shortcuts import bind_text_shortcuts

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """
    Главное окно приложения.
    """

    META_FORMATS = [
        "Standard",
        "Pioneer",
        "Explorer",
        "Modern",
        "Legacy",
        "Vintage",
        "Pauper",
        "Commander",
    ]

    def __init__(self):
        super().__init__()

        self.title("MTG AI Analyzer")
        self.geometry("1850x900")

        self.current_deck = None
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

        self.mtgdecks_url_entry = ctk.CTkEntry(
            self.top_panel,
            width=360,
            placeholder_text="URL MTGDecks...",
        )
        self.mtgdecks_url_entry.pack(side="left", padx=10, pady=10)

        bind_text_shortcuts(self.mtgdecks_url_entry)

        self.load_mtgdecks_button = ctk.CTkButton(
            self.top_panel,
            text="Загрузить URL",
            command=self.load_mtgdecks_url,
        )
        self.load_mtgdecks_button.pack(side="left", padx=5, pady=10)

        self.compare_mtgdecks_button = ctk.CTkButton(
            self.top_panel,
            text="Сравнить с URL",
            command=self.compare_mtgdecks_url,
        )
        self.compare_mtgdecks_button.pack(side="left", padx=5, pady=10)

        self.meta_format_combo = ctk.CTkComboBox(
            self.top_panel,
            values=self.META_FORMATS,
            width=150,
            state="readonly",
        )
        self.meta_format_combo.set("Pioneer")
        self.meta_format_combo.pack(side="left", padx=10, pady=10)

        self.load_meta_button = ctk.CTkButton(
            self.top_panel,
            text="Загрузить мету",
            command=self.load_selected_meta,
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

    # ======================================================
    # Card search
    # ======================================================

    def search_card(self, card_name):
        card_name = card_name.strip()

        if not card_name:
            self.status.label.configure(text="Введите название карты")
            return

        self.status.label.configure(text=f"Загрузка карты: {card_name}")

        self._run_background(
            target=self._search_card_worker,
            args=(card_name,),
        )

    def _search_card_worker(self, card_name):
        try:
            card = get_card(card_name)

            if card is None:
                self.after(
                    0,
                    self._on_card_not_found,
                )
                return

            image = load_card_image(card)

            self.after(
                0,
                self._on_card_loaded,
                card,
                image,
            )

        except Exception as error:
            self.after(
                0,
                self._on_card_error,
                str(error),
            )

    def _on_card_loaded(self, card, image):
        self.card_panel.show_card(card)
        self.image_panel.show_image(image)

        self.status.label.configure(text=f"Загружена карта: {card.name}")

    def _on_card_not_found(self):
        self.status.label.configure(text="Карта не найдена")

    def _on_card_error(self, message):
        self.status.label.configure(text=f"Ошибка загрузки карты: {message}")

    # ======================================================
    # Deck import
    # ======================================================

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

        bind_text_shortcuts(self.paste_textbox)

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

    def load_mtgdecks_url(self):
        url = self.mtgdecks_url_entry.get().strip()

        if not url:
            self.status.label.configure(text="Вставь ссылку MTGDecks")
            return

        self.analyze_deck_source(
            url,
            success_prefix="Колода загружена с MTGDecks.",
        )

    def analyze_deck_source(self, source, success_prefix):
        self.status.label.configure(text="Загрузка и анализ колоды...")

        self._set_deck_buttons_state("disabled")

        self._run_background(
            target=self._analyze_deck_worker,
            args=(source, success_prefix),
        )

    def _analyze_deck_worker(self, source, success_prefix):
        try:
            deck = ImportManager().load(source)

            analysis = DeckAnalyzer(deck).analyze()

            self.after(
                0,
                self._on_deck_loaded,
                deck,
                analysis,
                success_prefix,
            )

        except Exception as error:
            self.after(
                0,
                self._on_deck_error,
                str(error),
            )

    def _on_deck_loaded(self, deck, analysis, success_prefix):
        self.current_deck = deck

        self.deck_list_panel.show_deck(deck)
        self.deck_analysis_panel.show_analysis(analysis)

        self._set_deck_buttons_state("normal")

        self.status.label.configure(
            text=(
                f"{success_prefix} "
                f"Mainboard: {deck.mainboard_size}, "
                f"Sideboard: {deck.sideboard_size}"
            )
        )

    def _on_deck_error(self, message):
        self.deck_list_panel.show_error(message)
        self.deck_analysis_panel.show_error(message)

        self._set_deck_buttons_state("normal")

        self.status.label.configure(text="Ошибка загрузки колоды")

    # ======================================================
    # Deck compare
    # ======================================================

    def compare_mtgdecks_url(self):
        if self.current_deck is None:
            self.status.label.configure(text="Сначала загрузи свою колоду")
            return

        url = self.mtgdecks_url_entry.get().strip()

        if not url:
            self.status.label.configure(text="Вставь ссылку MTGDecks для сравнения")
            return

        self.meta_panel.show_compare_loading()

        self.status.label.configure(text="Сравнение с MTGDecks...")

        self._set_deck_buttons_state("disabled")

        self._run_background(
            target=self._compare_mtgdecks_worker,
            args=(
                self.current_deck,
                url,
            ),
        )

    def _compare_mtgdecks_worker(self, user_deck, url):
        try:
            reference_deck = ImportManager().load(url)

            comparison = MetaCompare().compare_all_zones(
                user_deck,
                reference_deck,
            )

            self.after(
                0,
                self._on_compare_loaded,
                comparison,
                user_deck,
                reference_deck,
            )

        except Exception as error:
            self.after(
                0,
                self._on_compare_error,
                str(error),
            )

    def _on_compare_loaded(
        self,
        comparison,
        user_deck,
        reference_deck,
    ):
        self.meta_panel.show_compare_result(
            comparison=comparison,
            user_deck=user_deck,
            reference_deck=reference_deck,
        )

        self._set_deck_buttons_state("normal")

        self.status.label.configure(
            text=f"Сравнение готово: {comparison.get('similarity', 0)}%"
        )

    def _on_compare_error(self, message):
        self.meta_panel.show_error(message)

        self._set_deck_buttons_state("normal")

        self.status.label.configure(text="Ошибка сравнения колод")

    # ======================================================
    # Meta loading
    # ======================================================

    def load_selected_meta(self):
        format_name = self.meta_format_combo.get()

        if not format_name:
            self.status.label.configure(text="Выбери формат меты")
            return

        self.meta_panel.show_loading(format_name)

        self.status.label.configure(text=f"Загрузка меты {format_name}...")

        self.load_meta_button.configure(state="disabled")
        self.meta_format_combo.configure(state="disabled")

        self._run_background(
            target=self._load_meta_worker,
            args=(format_name,),
        )

    def _load_meta_worker(self, format_name):
        try:
            provider = MTGDecksProvider()

            snapshot = provider.get_meta(format_name)

            self.after(
                0,
                self._on_meta_loaded,
                snapshot,
            )

        except Exception as error:
            self.after(
                0,
                self._on_meta_error,
                str(error),
            )

    def _on_meta_loaded(self, snapshot):
        self.meta_panel.show_snapshot(snapshot)

        self.load_meta_button.configure(state="normal")
        self.meta_format_combo.configure(state="readonly")

        self.status.label.configure(
            text=(
                f"Мета {snapshot.format_name} загружена. "
                f"Архетипов: {snapshot.count}"
            )
        )

    def _on_meta_error(self, message):
        self.meta_panel.show_error(message)

        self.load_meta_button.configure(state="normal")
        self.meta_format_combo.configure(state="readonly")

        self.status.label.configure(text="Ошибка загрузки меты")

    # ======================================================
    # Helpers
    # ======================================================

    def _set_deck_buttons_state(self, state):
        self.open_deck_button.configure(state=state)
        self.paste_deck_button.configure(state=state)
        self.load_mtgdecks_button.configure(state=state)
        self.compare_mtgdecks_button.configure(state=state)

    def _run_background(self, target, args=None):
        if args is None:
            args = ()

        thread = threading.Thread(
            target=target,
            args=args,
            daemon=True,
        )

        thread.start()
