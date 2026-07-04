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
from meta.deck_upgrade_builder import DeckUpgradeBuilder
from meta.meta_compare import MetaCompare
from providers.mtgdecks_provider import MTGDecksProvider
from services.deck_export_service import DeckExportService
from services.image_service import load_card_image
from utils.text_shortcuts import bind_text_shortcuts

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """
    Главное окно приложения.

    Интерфейс разбит на вкладки:
    - Поиск карт
    - Колода
    - Мета / Compare
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
        self.geometry("1500x900")
        self.minsize(1200, 750)

        self.current_deck = None
        self.last_reference_deck = None
        self.last_comparison = None
        self.last_upgraded_deck_text = None
        self.paste_window = None

        self.title_label = ctk.CTkLabel(
            self,
            text="MTG AI Analyzer",
            font=("Arial", 30, "bold"),
        )
        self.title_label.pack(pady=12)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 10),
        )

        self.search_tab = self.tabs.add("Поиск карт")
        self.deck_tab = self.tabs.add("Колода")
        self.meta_tab = self.tabs.add("Мета / Compare")

        self._build_search_tab()
        self._build_deck_tab()
        self._build_meta_tab()

        self.status = StatusBar(self)
        self.status.pack(
            fill="x",
            side="bottom",
        )

        self._set_deck_buttons_state("normal")

    # ======================================================
    # UI: Search tab
    # ======================================================

    def _build_search_tab(self):
        top_panel = ctk.CTkFrame(self.search_tab)
        top_panel.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        self.search_panel = SearchPanel(
            top_panel,
            self.search_card,
        )
        self.search_panel.pack(
            side="left",
            padx=10,
            pady=10,
        )

        content = ctk.CTkFrame(self.search_tab)
        content.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.image_panel = ImagePanel(content)
        self.image_panel.pack(
            side="left",
            fill="y",
            padx=10,
            pady=10,
        )

        self.card_panel = CardPanel(content)
        self.card_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

    # ======================================================
    # UI: Deck tab
    # ======================================================

    def _build_deck_tab(self):
        top_panel = ctk.CTkFrame(self.deck_tab)
        top_panel.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        self.open_deck_button = ctk.CTkButton(
            top_panel,
            text="Открыть колоду",
            command=self.open_deck_file,
            width=150,
        )
        self.open_deck_button.pack(
            side="left",
            padx=8,
            pady=10,
        )

        self.paste_deck_button = ctk.CTkButton(
            top_panel,
            text="Вставить колоду",
            command=self.open_paste_deck_window,
            width=150,
        )
        self.paste_deck_button.pack(
            side="left",
            padx=8,
            pady=10,
        )

        self.deck_mtgdecks_url_entry = ctk.CTkEntry(
            top_panel,
            width=460,
            placeholder_text="URL MTGDecks для загрузки колоды...",
        )
        self.deck_mtgdecks_url_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
            pady=10,
        )

        bind_text_shortcuts(self.deck_mtgdecks_url_entry)

        self.load_mtgdecks_button = ctk.CTkButton(
            top_panel,
            text="Загрузить URL",
            command=self.load_mtgdecks_url,
            width=140,
        )
        self.load_mtgdecks_button.pack(
            side="left",
            padx=8,
            pady=10,
        )

        content = ctk.CTkFrame(self.deck_tab)
        content.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.deck_list_panel = DeckListPanel(content)
        self.deck_list_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.deck_analysis_panel = DeckAnalysisPanel(content)
        self.deck_analysis_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

    # ======================================================
    # UI: Meta tab
    # ======================================================

    def _build_meta_tab(self):
        toolbar = ctk.CTkFrame(self.meta_tab)
        toolbar.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        # --------------------------------------------------
        # Строка загрузки меты
        # --------------------------------------------------

        meta_row = ctk.CTkFrame(toolbar)
        meta_row.pack(
            fill="x",
            padx=10,
            pady=(10, 5),
        )

        meta_label = ctk.CTkLabel(
            meta_row,
            text="Мета формата:",
            font=("Arial", 15, "bold"),
        )
        meta_label.pack(
            side="left",
            padx=8,
            pady=8,
        )

        self.meta_format_combo = ctk.CTkComboBox(
            meta_row,
            values=self.META_FORMATS,
            width=180,
            state="readonly",
        )
        self.meta_format_combo.set("Pioneer")
        self.meta_format_combo.pack(
            side="left",
            padx=8,
            pady=8,
        )

        self.load_meta_button = ctk.CTkButton(
            meta_row,
            text="Загрузить мету",
            command=self.load_selected_meta,
            width=160,
        )
        self.load_meta_button.pack(
            side="left",
            padx=8,
            pady=8,
        )

        # --------------------------------------------------
        # Строка сравнения
        # --------------------------------------------------

        compare_row = ctk.CTkFrame(toolbar)
        compare_row.pack(
            fill="x",
            padx=10,
            pady=5,
        )

        compare_label = ctk.CTkLabel(
            compare_row,
            text="Эталонная колода:",
            font=("Arial", 15, "bold"),
        )
        compare_label.pack(
            side="left",
            padx=8,
            pady=8,
        )

        self.compare_mtgdecks_url_entry = ctk.CTkEntry(
            compare_row,
            width=600,
            placeholder_text="URL MTGDecks для сравнения...",
        )
        self.compare_mtgdecks_url_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
            pady=8,
        )

        bind_text_shortcuts(self.compare_mtgdecks_url_entry)

        self.compare_mtgdecks_button = ctk.CTkButton(
            compare_row,
            text="Сравнить с URL",
            command=self.compare_mtgdecks_url,
            width=160,
        )
        self.compare_mtgdecks_button.pack(
            side="left",
            padx=8,
            pady=8,
        )

        # --------------------------------------------------
        # Строка действий с обновлённой колодой
        # --------------------------------------------------

        actions_row = ctk.CTkFrame(toolbar)
        actions_row.pack(
            fill="x",
            padx=10,
            pady=(5, 10),
        )

        actions_label = ctk.CTkLabel(
            actions_row,
            text="Обновлённая колода:",
            font=("Arial", 15, "bold"),
        )
        actions_label.pack(
            side="left",
            padx=8,
            pady=8,
        )

        self.build_upgraded_deck_button = ctk.CTkButton(
            actions_row,
            text="Сформировать колоду",
            command=self.build_upgraded_deck,
            width=190,
        )
        self.build_upgraded_deck_button.pack(
            side="left",
            padx=8,
            pady=8,
        )

        self.copy_upgraded_deck_button = ctk.CTkButton(
            actions_row,
            text="Копировать колоду",
            command=self.copy_upgraded_deck,
            width=180,
        )
        self.copy_upgraded_deck_button.pack(
            side="left",
            padx=8,
            pady=8,
        )

        self.save_upgraded_deck_button = ctk.CTkButton(
            actions_row,
            text="Сохранить колоду",
            command=self.save_upgraded_deck,
            width=180,
        )
        self.save_upgraded_deck_button.pack(
            side="left",
            padx=8,
            pady=8,
        )

        content = ctk.CTkFrame(self.meta_tab)
        content.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.meta_panel = MetaPanel(content)
        self.meta_panel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

    # ======================================================
    # Card search
    # ======================================================

    def search_card(self, card_name):
        card_name = card_name.strip()

        if not card_name:
            self.status.label.configure(text="Введите название карты")
            return

        self.tabs.set("Поиск карт")

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
        self.paste_window.geometry("750x620")

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
            width=700,
            height=420,
        )
        self.paste_textbox.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10,
        )

        bind_text_shortcuts(self.paste_textbox)

        buttons_panel = ctk.CTkFrame(self.paste_window)
        buttons_panel.pack(
            fill="x",
            padx=20,
            pady=15,
        )

        analyze_button = ctk.CTkButton(
            buttons_panel,
            text="Анализировать",
            command=self.analyze_pasted_deck,
        )
        analyze_button.pack(
            side="left",
            padx=10,
        )

        close_button = ctk.CTkButton(
            buttons_panel,
            text="Закрыть",
            command=self.paste_window.destroy,
        )
        close_button.pack(
            side="left",
            padx=10,
        )

        example_button = ctk.CTkButton(
            buttons_panel,
            text="Вставить пример",
            command=self.insert_example_deck,
        )
        example_button.pack(
            side="left",
            padx=10,
        )

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
        url = self.deck_mtgdecks_url_entry.get().strip()

        if not url:
            self.status.label.configure(
                text="Вставь ссылку MTGDecks для загрузки колоды"
            )
            return

        self.analyze_deck_source(
            url,
            success_prefix="Колода загружена с MTGDecks.",
        )

    def analyze_deck_source(self, source, success_prefix):
        self.tabs.set("Колода")

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

        self.last_reference_deck = None
        self.last_comparison = None
        self.last_upgraded_deck_text = None

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

        url = self.compare_mtgdecks_url_entry.get().strip()

        if not url:
            self.status.label.configure(text="Вставь ссылку MTGDecks для сравнения")
            return

        self.last_reference_deck = None
        self.last_comparison = None
        self.last_upgraded_deck_text = None

        self.tabs.set("Мета / Compare")

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
        self.last_comparison = comparison
        self.last_reference_deck = reference_deck
        self.last_upgraded_deck_text = None

        self.meta_panel.show_compare_result(
            comparison=comparison,
            user_deck=user_deck,
            reference_deck=reference_deck,
        )

        self._set_deck_buttons_state("normal")

        self.status.label.configure(
            text=f"Сравнение готово: {comparison.get('overall_similarity', 0)}%"
        )

    def _on_compare_error(self, message):
        self.meta_panel.show_error(message)

        self._set_deck_buttons_state("normal")

        self.status.label.configure(text="Ошибка сравнения колод")

    # ======================================================
    # Deck upgrade
    # ======================================================

    def build_upgraded_deck(self):
        if self.current_deck is None:
            self.status.label.configure(text="Сначала загрузи свою колоду")
            return

        if self.last_reference_deck is None or self.last_comparison is None:
            self.status.label.configure(text="Сначала выполни сравнение с MTGDecks URL")
            return

        self.tabs.set("Мета / Compare")

        deck_text = DeckUpgradeBuilder().build_upgraded_deck_text(
            user_deck=self.current_deck,
            reference_deck=self.last_reference_deck,
            comparison=self.last_comparison,
        )

        self.last_upgraded_deck_text = deck_text

        self.meta_panel.show_upgraded_deck_text(deck_text)

        self._update_action_button_states()

        self.status.label.configure(text="Обновлённая колода сформирована")

    def copy_upgraded_deck(self):
        if not self.last_upgraded_deck_text:
            self.status.label.configure(text="Сначала сформируй обновлённую колоду")
            return

        try:
            self.clipboard_clear()

            self.clipboard_append(self.last_upgraded_deck_text)

            self.update_idletasks()

            self.status.label.configure(
                text="Обновлённая колода скопирована в буфер обмена"
            )

        except Exception as error:
            self.status.label.configure(text=f"Ошибка копирования колоды: {error}")

    def save_upgraded_deck(self):
        if not self.last_upgraded_deck_text:
            self.status.label.configure(text="Сначала сформируй обновлённую колоду")
            return

        try:
            path = DeckExportService().save_deck_text(
                deck_text=self.last_upgraded_deck_text,
                filename="upgraded_deck.txt",
                folder="decks",
            )

            self.status.label.configure(text=f"Колода сохранена: {path}")

        except Exception as error:
            self.status.label.configure(text=f"Ошибка сохранения колоды: {error}")

    # ======================================================
    # Meta loading
    # ======================================================

    def load_selected_meta(self):
        format_name = self.meta_format_combo.get()

        if not format_name:
            self.status.label.configure(text="Выбери формат меты")
            return

        self.tabs.set("Мета / Compare")

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

        if state == "disabled":
            self.compare_mtgdecks_button.configure(state="disabled")
            self.build_upgraded_deck_button.configure(state="disabled")
            self.copy_upgraded_deck_button.configure(state="disabled")
            self.save_upgraded_deck_button.configure(state="disabled")
            return

        self._update_action_button_states()

    def _update_action_button_states(self):
        if self.current_deck is None:
            self.compare_mtgdecks_button.configure(state="disabled")
        else:
            self.compare_mtgdecks_button.configure(state="normal")

        if self.last_reference_deck is None or self.last_comparison is None:
            self.build_upgraded_deck_button.configure(state="disabled")
        else:
            self.build_upgraded_deck_button.configure(state="normal")

        if not self.last_upgraded_deck_text:
            self.copy_upgraded_deck_button.configure(state="disabled")
            self.save_upgraded_deck_button.configure(state="disabled")
        else:
            self.copy_upgraded_deck_button.configure(state="normal")
            self.save_upgraded_deck_button.configure(state="normal")

    def _run_background(self, target, args=None):
        if args is None:
            args = ()

        thread = threading.Thread(
            target=target,
            args=args,
            daemon=True,
        )

        thread.start()
