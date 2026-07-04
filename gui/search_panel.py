import threading
import tkinter as tk
import webbrowser

import customtkinter as ctk

from api.scryfall_search import ScryfallSearchClient
from services.scryfall_query_builder import ScryfallQueryBuilder
from utils.text_shortcuts import bind_text_shortcuts


class SearchPanel(ctk.CTkFrame):
    """
    Рабочая область поиска карт через Scryfall.

    Внутренние вкладки:
    - Быстрый поиск;
    - Расширенный поиск;
    - ALL SET;
    - Результаты.

    search_callback получает название выбранной карты.
    Главное окно затем загружает изображение и полную информацию.
    """

    QUICK_TAB = "Быстрый поиск"
    ADVANCED_TAB = "Расширенный поиск"
    SETS_TAB = "ALL SET"
    RESULTS_TAB = "Результаты"

    COLOR_VALUES = (
        "W",
        "U",
        "B",
        "R",
        "G",
        "C",
    )

    FORMAT_VALUES = [
        "any",
        "standard",
        "future",
        "historic",
        "timeless",
        "gladiator",
        "pioneer",
        "explorer",
        "modern",
        "legacy",
        "pauper",
        "vintage",
        "penny",
        "commander",
        "oathbreaker",
        "standardbrawl",
        "brawl",
        "alchemy",
        "paupercommander",
        "duel",
        "oldschool",
        "premodern",
        "predh",
    ]

    GAME_VALUES = [
        "any",
        "paper",
        "arena",
        "mtgo",
    ]

    LANGUAGE_VALUES = [
        "any",
        "en",
        "ru",
        "de",
        "fr",
        "es",
        "it",
        "pt",
        "ja",
        "ko",
        "zhs",
        "zht",
        "he",
        "la",
        "grc",
        "ar",
        "sa",
        "ph",
    ]

    UNIQUE_VALUES = [
        "cards",
        "art",
        "prints",
    ]

    ORDER_VALUES = [
        "name",
        "set",
        "released",
        "rarity",
        "color",
        "usd",
        "tix",
        "eur",
        "cmc",
        "power",
        "toughness",
        "edhrec",
        "penny",
        "artist",
        "review",
    ]

    DIRECTION_VALUES = [
        "auto",
        "asc",
        "desc",
    ]

    OPERATOR_VALUES = [
        "=",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
    ]

    SET_SORT_VALUES = [
        "release date",
        "name",
        "cards",
        "type",
    ]

    def __init__(
        self,
        master,
        search_callback,
    ):
        super().__init__(
            master,
            height=395,
        )

        self.search_callback = search_callback

        self.client = ScryfallSearchClient()

        self.current_query = ""
        self.current_page = 1
        self.current_options = {}

        self.result_cards = []
        self.has_more_results = False

        self.all_sets = []
        self.filtered_sets = []

        self.sets_loaded = False
        self.sets_loading = False
        self.search_running = False

        self.advanced_entries = {}
        self.advanced_combos = {}

        self.color_variables = {}
        self.identity_variables = {}

        self.pack_propagate(False)

        self.tabs = ctk.CTkTabview(
            self,
            command=self._on_tab_changed,
        )
        self.tabs.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8,
        )

        self.quick_tab = self.tabs.add(self.QUICK_TAB)
        self.advanced_tab = self.tabs.add(self.ADVANCED_TAB)
        self.sets_tab = self.tabs.add(self.SETS_TAB)
        self.results_tab = self.tabs.add(self.RESULTS_TAB)

        self._build_quick_tab()
        self._build_advanced_tab()
        self._build_sets_tab()
        self._build_results_tab()

        self.tabs.set(self.QUICK_TAB)

        self.master.bind(
            "<Configure>",
            self._sync_width_with_parent,
            add="+",
        )

    # ======================================================
    # Общая компоновка
    # ======================================================

    def _sync_width_with_parent(self, event):
        if event.width < 200:
            return

        self.configure(
            width=max(
                800,
                event.width - 20,
            )
        )

    def _on_tab_changed(self):
        selected_tab = self.tabs.get()

        if (
            selected_tab == self.SETS_TAB
            and not self.sets_loaded
            and not self.sets_loading
        ):
            self.load_sets()

    # ======================================================
    # Быстрый поиск
    # ======================================================

    def _build_quick_tab(self):
        content = ctk.CTkFrame(self.quick_tab)
        content.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        title = ctk.CTkLabel(
            content,
            text="Поиск карт Scryfall",
            font=("Arial", 22, "bold"),
        )
        title.pack(
            pady=(18, 6),
        )

        description = ctk.CTkLabel(
            content,
            text=(
                "Можно вводить название карты или полноценный "
                "поисковый запрос Scryfall."
            ),
        )
        description.pack(
            pady=(0, 15),
        )

        search_row = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )
        search_row.pack(
            fill="x",
            padx=30,
            pady=5,
        )

        self.quick_query_entry = ctk.CTkEntry(
            search_row,
            height=42,
            placeholder_text=(
                "Пример: Aang или " "type:creature color<=WU legal:pioneer"
            ),
        )
        self.quick_query_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10),
        )

        bind_text_shortcuts(self.quick_query_entry)

        self.quick_query_entry.bind(
            "<Return>",
            lambda event: self.search_quick(),
        )

        self.quick_search_button = ctk.CTkButton(
            search_row,
            text="Найти карты",
            command=self.search_quick,
            width=150,
            height=42,
        )
        self.quick_search_button.pack(
            side="left",
        )

        buttons_row = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )
        buttons_row.pack(
            pady=12,
        )

        self.random_card_button = ctk.CTkButton(
            buttons_row,
            text="Случайная карта",
            command=self.load_random_card,
            width=160,
        )
        self.random_card_button.pack(
            side="left",
            padx=6,
        )

        syntax_button = ctk.CTkButton(
            buttons_row,
            text="Синтаксис Scryfall",
            command=self.open_scryfall_syntax,
            width=170,
        )
        syntax_button.pack(
            side="left",
            padx=6,
        )

        clear_button = ctk.CTkButton(
            buttons_row,
            text="Очистить",
            command=self.clear_quick_search,
            width=120,
        )
        clear_button.pack(
            side="left",
            padx=6,
        )

        examples = ctk.CTkLabel(
            content,
            text=(
                "Примеры:\n"
                "legal:pioneer type:creature\n"
                'oracle:"draw a card" color<=UB\n'
                "set:tla rarity:mythic"
            ),
            justify="left",
        )
        examples.pack(
            pady=(10, 5),
        )

        self.quick_status_label = ctk.CTkLabel(
            content,
            text="Готово",
        )
        self.quick_status_label.pack(
            pady=(8, 5),
        )

    def search_quick(self):
        query = self.quick_query_entry.get().strip()

        if not query:
            self._set_status("Введите название карты или запрос")
            return

        self.start_search(
            query=query,
            page=1,
            unique="cards",
            order="name",
            direction="auto",
            include_extras=False,
        )

    def clear_quick_search(self):
        self.quick_query_entry.delete(
            0,
            "end",
        )

        self._set_status("Готово")

    def open_scryfall_syntax(self):
        webbrowser.open("https://scryfall.com/docs/syntax")

    # ======================================================
    # Расширенный поиск
    # ======================================================

    def _build_advanced_tab(self):
        form = ctk.CTkScrollableFrame(
            self.advanced_tab,
            fg_color="transparent",
        )
        form.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=6,
        )

        form.grid_columnconfigure(
            0,
            weight=1,
        )
        form.grid_columnconfigure(
            1,
            weight=1,
        )

        text_section = self._create_section(
            parent=form,
            title="Текст карты",
            row=0,
            column=0,
        )

        self._add_entry(
            text_section,
            key="raw_query",
            label="Дополнительный запрос",
            placeholder=("Например: -is:funny border:black"),
        )

        self._add_entry(
            text_section,
            key="name",
            label="Название карты",
            placeholder="Например: Aang",
        )

        self._add_entry(
            text_section,
            key="oracle",
            label="Oracle-текст",
            placeholder="Например: draw a card",
        )

        self._add_entry(
            text_section,
            key="flavor",
            label="Художественный текст",
            placeholder="Flavor text",
        )

        type_section = self._create_section(
            parent=form,
            title="Тип карты",
            row=0,
            column=1,
        )

        self._add_entry(
            type_section,
            key="type_line",
            label="Строка типа",
            placeholder=("Например: Legendary Creature"),
        )

        self._add_entry(
            type_section,
            key="types",
            label="Типы через запятую",
            placeholder=("creature, artifact, instant"),
        )

        self._add_entry(
            type_section,
            key="criteria",
            label="Критерии is: через запятую",
            placeholder=("legendary, booster, commander"),
        )

        self._add_entry(
            type_section,
            key="artist",
            label="Художник",
            placeholder="Имя художника",
        )

        self._add_entry(
            type_section,
            key="lore",
            label="Lore",
            placeholder="Lore search",
        )

        color_section = self._create_section(
            parent=form,
            title="Цвета и Commander",
            row=1,
            column=0,
        )

        color_comparison_row = ctk.CTkFrame(
            color_section,
            fg_color="transparent",
        )
        color_comparison_row.pack(
            fill="x",
            padx=10,
            pady=(8, 2),
        )

        color_label = ctk.CTkLabel(
            color_comparison_row,
            text="Цвета карты",
            width=150,
            anchor="w",
        )
        color_label.pack(
            side="left",
        )

        self.color_comparison_combo = ctk.CTkComboBox(
            color_comparison_row,
            values=[
                "=",
                ">=",
                "<=",
            ],
            width=90,
            state="readonly",
        )
        self.color_comparison_combo.set("=")
        self.color_comparison_combo.pack(
            side="left",
            padx=5,
        )

        colors_row = ctk.CTkFrame(
            color_section,
            fg_color="transparent",
        )
        colors_row.pack(
            fill="x",
            padx=10,
            pady=(2, 10),
        )

        for color in self.COLOR_VALUES:
            variable = tk.BooleanVar(value=False)

            checkbox = ctk.CTkCheckBox(
                colors_row,
                text=color,
                variable=variable,
                width=55,
            )
            checkbox.pack(
                side="left",
                padx=4,
            )

            self.color_variables[color] = variable

        identity_comparison_row = ctk.CTkFrame(
            color_section,
            fg_color="transparent",
        )
        identity_comparison_row.pack(
            fill="x",
            padx=10,
            pady=(5, 2),
        )

        identity_label = ctk.CTkLabel(
            identity_comparison_row,
            text="Commander identity",
            width=150,
            anchor="w",
        )
        identity_label.pack(
            side="left",
        )

        self.identity_comparison_combo = ctk.CTkComboBox(
            identity_comparison_row,
            values=[
                "=",
                ">=",
                "<=",
            ],
            width=90,
            state="readonly",
        )
        self.identity_comparison_combo.set("<=")
        self.identity_comparison_combo.pack(
            side="left",
            padx=5,
        )

        identity_row = ctk.CTkFrame(
            color_section,
            fg_color="transparent",
        )
        identity_row.pack(
            fill="x",
            padx=10,
            pady=(2, 10),
        )

        for color in self.COLOR_VALUES:
            variable = tk.BooleanVar(value=False)

            checkbox = ctk.CTkCheckBox(
                identity_row,
                text=color,
                variable=variable,
                width=55,
            )
            checkbox.pack(
                side="left",
                padx=4,
            )

            self.identity_variables[color] = variable

        mana_section = self._create_section(
            parent=form,
            title="Мана и характеристики",
            row=1,
            column=1,
        )

        self._add_entry(
            mana_section,
            key="mana_cost",
            label="Стоимость маны",
            placeholder="{1}{W}{U}",
        )

        self._add_operator_entry(
            mana_section,
            entry_key="mana_value",
            combo_key="mana_value_operator",
            label="Mana Value",
            default_operator="=",
        )

        self._add_operator_entry(
            mana_section,
            entry_key="power",
            combo_key="power_operator",
            label="Сила",
            default_operator="=",
        )

        self._add_operator_entry(
            mana_section,
            entry_key="toughness",
            combo_key="toughness_operator",
            label="Выносливость",
            default_operator="=",
        )

        self._add_operator_entry(
            mana_section,
            entry_key="loyalty",
            combo_key="loyalty_operator",
            label="Лояльность",
            default_operator="=",
        )

        format_section = self._create_section(
            parent=form,
            title="Формат и выпуск",
            row=2,
            column=0,
        )

        self._add_combo(
            format_section,
            key="game",
            label="Игра",
            values=self.GAME_VALUES,
            default="any",
        )

        self._add_combo(
            format_section,
            key="format_status",
            label="Статус в формате",
            values=[
                "legal",
                "banned",
                "restricted",
            ],
            default="legal",
        )

        self._add_combo(
            format_section,
            key="format",
            label="Формат",
            values=self.FORMAT_VALUES,
            default="any",
        )

        self._add_entry(
            format_section,
            key="sets",
            label="Коды наборов через запятую",
            placeholder="tla, mkm, dft",
        )

        self._add_entry(
            format_section,
            key="rarities",
            label="Редкости через запятую",
            placeholder="common, rare, mythic",
        )

        additional_section = self._create_section(
            parent=form,
            title="Дополнительные параметры",
            row=2,
            column=1,
        )

        self._add_combo(
            additional_section,
            key="language",
            label="Язык",
            values=self.LANGUAGE_VALUES,
            default="any",
        )

        price_row = ctk.CTkFrame(
            additional_section,
            fg_color="transparent",
        )
        price_row.pack(
            fill="x",
            padx=10,
            pady=8,
        )

        price_label = ctk.CTkLabel(
            price_row,
            text="Цена",
            width=120,
            anchor="w",
        )
        price_label.pack(
            side="left",
        )

        self.advanced_combos["price_currency"] = ctk.CTkComboBox(
            price_row,
            values=[
                "usd",
                "eur",
                "tix",
            ],
            width=90,
            state="readonly",
        )
        self.advanced_combos["price_currency"].set("usd")
        self.advanced_combos["price_currency"].pack(
            side="left",
            padx=4,
        )

        self.advanced_combos["price_operator"] = ctk.CTkComboBox(
            price_row,
            values=self.OPERATOR_VALUES,
            width=80,
            state="readonly",
        )
        self.advanced_combos["price_operator"].set("<=")
        self.advanced_combos["price_operator"].pack(
            side="left",
            padx=4,
        )

        price_entry = ctk.CTkEntry(
            price_row,
            placeholder_text="10",
        )
        price_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(4, 0),
        )

        bind_text_shortcuts(price_entry)

        self.advanced_entries["price_value"] = price_entry

        self._add_combo(
            additional_section,
            key="unique",
            label="Уникальность",
            values=self.UNIQUE_VALUES,
            default="cards",
        )

        self._add_combo(
            additional_section,
            key="order",
            label="Сортировка",
            values=self.ORDER_VALUES,
            default="name",
        )

        self._add_combo(
            additional_section,
            key="direction",
            label="Направление",
            values=self.DIRECTION_VALUES,
            default="auto",
        )

        self.include_extras_switch = ctk.CTkSwitch(
            additional_section,
            text="Включать extras и tokens",
        )
        self.include_extras_switch.pack(
            anchor="w",
            padx=10,
            pady=10,
        )

        actions_section = self._create_section(
            parent=form,
            title="Запрос",
            row=3,
            column=0,
            columnspan=2,
        )

        buttons_row = ctk.CTkFrame(
            actions_section,
            fg_color="transparent",
        )
        buttons_row.pack(
            pady=(8, 5),
        )

        build_query_button = ctk.CTkButton(
            buttons_row,
            text="Собрать запрос",
            command=self.build_advanced_query,
            width=160,
        )
        build_query_button.pack(
            side="left",
            padx=6,
        )

        self.advanced_search_button = ctk.CTkButton(
            buttons_row,
            text="Найти карты",
            command=self.search_advanced,
            width=160,
        )
        self.advanced_search_button.pack(
            side="left",
            padx=6,
        )

        reset_button = ctk.CTkButton(
            buttons_row,
            text="Сбросить фильтры",
            command=self.reset_advanced_form,
            width=170,
        )
        reset_button.pack(
            side="left",
            padx=6,
        )

        self.advanced_query_textbox = ctk.CTkTextbox(
            actions_section,
            height=65,
        )
        self.advanced_query_textbox.pack(
            fill="x",
            padx=10,
            pady=(5, 10),
        )

        bind_text_shortcuts(self.advanced_query_textbox)

    def _create_section(
        self,
        parent,
        title,
        row,
        column,
        columnspan=1,
    ):
        section = ctk.CTkFrame(parent)

        section.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=("Arial", 16, "bold"),
        )
        title_label.pack(
            anchor="w",
            padx=10,
            pady=(10, 3),
        )

        return section

    def _add_entry(
        self,
        parent,
        key,
        label,
        placeholder="",
    ):
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            anchor="w",
        )
        label_widget.pack(
            fill="x",
            padx=10,
            pady=(6, 2),
        )

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
        )
        entry.pack(
            fill="x",
            padx=10,
            pady=(0, 6),
        )

        bind_text_shortcuts(entry)

        self.advanced_entries[key] = entry

        return entry

    def _add_combo(
        self,
        parent,
        key,
        label,
        values,
        default,
    ):
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        row.pack(
            fill="x",
            padx=10,
            pady=6,
        )

        label_widget = ctk.CTkLabel(
            row,
            text=label,
            width=150,
            anchor="w",
        )
        label_widget.pack(
            side="left",
        )

        combo = ctk.CTkComboBox(
            row,
            values=values,
            state="readonly",
        )
        combo.set(default)
        combo.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.advanced_combos[key] = combo

        return combo

    def _add_operator_entry(
        self,
        parent,
        entry_key,
        combo_key,
        label,
        default_operator,
    ):
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        row.pack(
            fill="x",
            padx=10,
            pady=6,
        )

        label_widget = ctk.CTkLabel(
            row,
            text=label,
            width=120,
            anchor="w",
        )
        label_widget.pack(
            side="left",
        )

        combo = ctk.CTkComboBox(
            row,
            values=self.OPERATOR_VALUES,
            width=80,
            state="readonly",
        )
        combo.set(default_operator)
        combo.pack(
            side="left",
            padx=(0, 6),
        )

        entry = ctk.CTkEntry(row)
        entry.pack(
            side="left",
            fill="x",
            expand=True,
        )

        bind_text_shortcuts(entry)

        self.advanced_combos[combo_key] = combo

        self.advanced_entries[entry_key] = entry

    def build_advanced_query(self):
        filters = self._collect_advanced_filters()

        query = ScryfallQueryBuilder.build(filters)

        self._set_advanced_query_text(query)

        if query:
            self._set_status("Поисковый запрос сформирован")
        else:
            self._set_status("Заполните хотя бы один фильтр")

        return query

    def search_advanced(self):
        query = self.build_advanced_query()

        if not query:
            return

        unique = self.advanced_combos["unique"].get()

        order = self.advanced_combos["order"].get()

        direction = self.advanced_combos["direction"].get()

        include_extras = bool(self.include_extras_switch.get())

        self.start_search(
            query=query,
            page=1,
            unique=unique,
            order=order,
            direction=direction,
            include_extras=include_extras,
        )

    def _collect_advanced_filters(self):
        colors = [
            color for color, variable in self.color_variables.items() if variable.get()
        ]

        identity = [
            color
            for color, variable in self.identity_variables.items()
            if variable.get()
        ]

        game = self.advanced_combos["game"].get()

        format_name = self.advanced_combos["format"].get()

        language = self.advanced_combos["language"].get()

        return {
            "raw_query": self._entry_value("raw_query"),
            "name": self._entry_value("name"),
            "oracle": self._entry_value("oracle"),
            "flavor": self._entry_value("flavor"),
            "lore": self._entry_value("lore"),
            "type_line": self._entry_value("type_line"),
            "types": self._split_values(self._entry_value("types")),
            "criteria": self._split_values(self._entry_value("criteria")),
            "artist": self._entry_value("artist"),
            "colors": colors,
            "color_comparison": (self.color_comparison_combo.get()),
            "identity": identity,
            "identity_comparison": (self.identity_comparison_combo.get()),
            "mana_cost": self._entry_value("mana_cost"),
            "mana_value": self._entry_value("mana_value"),
            "mana_value_operator": (self.advanced_combos["mana_value_operator"].get()),
            "power": self._entry_value("power"),
            "power_operator": (self.advanced_combos["power_operator"].get()),
            "toughness": self._entry_value("toughness"),
            "toughness_operator": (self.advanced_combos["toughness_operator"].get()),
            "loyalty": self._entry_value("loyalty"),
            "loyalty_operator": (self.advanced_combos["loyalty_operator"].get()),
            "games": ([] if game == "any" else [game]),
            "format_status": (self.advanced_combos["format_status"].get()),
            "format": ("" if format_name == "any" else format_name),
            "sets": self._split_values(self._entry_value("sets")),
            "rarities": self._split_values(self._entry_value("rarities")),
            "language": ("" if language == "any" else language),
            "price_currency": (self.advanced_combos["price_currency"].get()),
            "price_operator": (self.advanced_combos["price_operator"].get()),
            "price_value": self._entry_value("price_value"),
        }

    def reset_advanced_form(self):
        for entry in self.advanced_entries.values():
            entry.delete(
                0,
                "end",
            )

        defaults = {
            "game": "any",
            "format_status": "legal",
            "format": "any",
            "language": "any",
            "price_currency": "usd",
            "price_operator": "<=",
            "unique": "cards",
            "order": "name",
            "direction": "auto",
            "mana_value_operator": "=",
            "power_operator": "=",
            "toughness_operator": "=",
            "loyalty_operator": "=",
        }

        for key, value in defaults.items():
            combo = self.advanced_combos.get(key)

            if combo is not None:
                combo.set(value)

        self.color_comparison_combo.set("=")
        self.identity_comparison_combo.set("<=")

        for variable in self.color_variables.values():
            variable.set(False)

        for variable in self.identity_variables.values():
            variable.set(False)

        self.include_extras_switch.deselect()

        self._set_advanced_query_text("")

        self._set_status("Фильтры расширенного поиска сброшены")

    def _set_advanced_query_text(self, query):
        self.advanced_query_textbox.delete(
            "1.0",
            "end",
        )

        if query:
            self.advanced_query_textbox.insert(
                "1.0",
                query,
            )

    # ======================================================
    # ALL SET
    # ======================================================

    def _build_sets_tab(self):
        controls = ctk.CTkFrame(self.sets_tab)
        controls.pack(
            fill="x",
            padx=8,
            pady=8,
        )

        self.set_name_entry = ctk.CTkEntry(
            controls,
            placeholder_text=("Название или код набора..."),
            width=300,
        )
        self.set_name_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=6,
            pady=8,
        )

        bind_text_shortcuts(self.set_name_entry)

        self.set_name_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh_sets_list(),
        )

        self.set_language_combo = ctk.CTkComboBox(
            controls,
            values=self.LANGUAGE_VALUES,
            width=110,
            state="readonly",
            command=lambda value: (self.refresh_sets_list()),
        )
        self.set_language_combo.set("any")
        self.set_language_combo.pack(
            side="left",
            padx=6,
            pady=8,
        )

        self.set_type_combo = ctk.CTkComboBox(
            controls,
            values=["any"],
            width=180,
            state="readonly",
            command=lambda value: (self.refresh_sets_list()),
        )
        self.set_type_combo.set("any")
        self.set_type_combo.pack(
            side="left",
            padx=6,
            pady=8,
        )

        self.set_sort_combo = ctk.CTkComboBox(
            controls,
            values=self.SET_SORT_VALUES,
            width=150,
            state="readonly",
            command=lambda value: (self.refresh_sets_list()),
        )
        self.set_sort_combo.set("release date")
        self.set_sort_combo.pack(
            side="left",
            padx=6,
            pady=8,
        )

        self.reload_sets_button = ctk.CTkButton(
            controls,
            text="Обновить",
            command=self.reload_sets,
            width=110,
        )
        self.reload_sets_button.pack(
            side="left",
            padx=6,
            pady=8,
        )

        list_frame = ctk.CTkFrame(self.sets_tab)
        list_frame.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8),
        )

        scrollbar = tk.Scrollbar(
            list_frame,
            orient="vertical",
        )
        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.sets_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#1f1f1f",
            fg="#eeeeee",
            selectbackground="#1f6aa5",
            selectforeground="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 11),
            activestyle="none",
        )
        self.sets_listbox.pack(
            side="left",
            fill="both",
            expand=True,
            padx=4,
            pady=4,
        )

        scrollbar.configure(command=self.sets_listbox.yview)

        self.sets_listbox.bind(
            "<Double-Button-1>",
            lambda event: self.open_selected_set(),
        )

        self.sets_listbox.bind(
            "<Return>",
            lambda event: self.open_selected_set(),
        )

        bottom_row = ctk.CTkFrame(
            self.sets_tab,
            fg_color="transparent",
        )
        bottom_row.pack(
            fill="x",
            padx=8,
            pady=(0, 8),
        )

        self.sets_status_label = ctk.CTkLabel(
            bottom_row,
            text=("Наборы ещё не загружены"),
            anchor="w",
        )
        self.sets_status_label.pack(
            side="left",
            fill="x",
            expand=True,
        )

        open_set_button = ctk.CTkButton(
            bottom_row,
            text="Показать карты набора",
            command=self.open_selected_set,
            width=190,
        )
        open_set_button.pack(
            side="right",
        )

    def load_sets(self):
        if self.sets_loading:
            return

        self.sets_loading = True

        self.sets_status_label.configure(text="Загрузка наборов Scryfall...")

        self.reload_sets_button.configure(state="disabled")

        self._run_background(self._load_sets_worker)

    def reload_sets(self):
        self.sets_loaded = False
        self.all_sets = []
        self.filtered_sets = []

        self.load_sets()

    def _load_sets_worker(self):
        try:
            sets = self.client.get_all_sets()

            self.after(
                0,
                self._on_sets_loaded,
                sets,
            )

        except Exception as error:
            self.after(
                0,
                self._on_sets_error,
                str(error),
            )

    def _on_sets_loaded(self, sets):
        self.all_sets = sets
        self.sets_loaded = True
        self.sets_loading = False

        set_types = sorted(
            {item.get("set_type", "") for item in sets if item.get("set_type")}
        )

        self.set_type_combo.configure(
            values=[
                "any",
                *set_types,
            ]
        )
        self.set_type_combo.set("any")

        self.reload_sets_button.configure(state="normal")

        self.refresh_sets_list()

    def _on_sets_error(self, message):
        self.sets_loading = False

        self.reload_sets_button.configure(state="normal")

        self.sets_status_label.configure(
            text=("Ошибка загрузки наборов: " f"{message}")
        )

    def refresh_sets_list(self):
        if not self.sets_loaded:
            return

        search_text = self.set_name_entry.get().strip().lower()

        set_type = self.set_type_combo.get()
        sort_mode = self.set_sort_combo.get()

        filtered = []

        for set_data in self.all_sets:
            name = str(set_data.get("name", ""))
            code = str(set_data.get("code", ""))
            current_type = str(set_data.get("set_type", ""))

            if search_text:
                if search_text not in name.lower() and search_text not in code.lower():
                    continue

            if set_type != "any" and current_type != set_type:
                continue

            filtered.append(set_data)

        if sort_mode == "name":
            filtered.sort(key=lambda item: (str(item.get("name", "")).lower()))

        elif sort_mode == "cards":
            filtered.sort(
                key=lambda item: int(item.get("card_count", 0) or 0),
                reverse=True,
            )

        elif sort_mode == "type":
            filtered.sort(
                key=lambda item: (
                    str(item.get("set_type", "")),
                    str(item.get("name", "")).lower(),
                )
            )

        else:
            filtered.sort(
                key=lambda item: str(item.get("released_at", "") or ""),
                reverse=True,
            )

        self.filtered_sets = filtered

        self.sets_listbox.delete(
            0,
            "end",
        )

        for set_data in filtered:
            code = str(set_data.get("code", "")).upper()

            name = str(set_data.get("name", ""))

            set_type_value = str(set_data.get("set_type", ""))

            cards = int(set_data.get("card_count", 0) or 0)

            released_at = str(set_data.get("released_at", "") or "—")

            line = (
                f"{code:<8} "
                f"{name:<48} "
                f"{set_type_value:<18} "
                f"{cards:>5}  "
                f"{released_at}"
            )

            self.sets_listbox.insert(
                "end",
                line,
            )

        self.sets_status_label.configure(
            text=(f"Показано наборов: " f"{len(filtered)} из " f"{len(self.all_sets)}")
        )

    def open_selected_set(self):
        selection = self.sets_listbox.curselection()

        if not selection:
            self.sets_status_label.configure(text="Выберите набор")
            return

        index = selection[0]

        if index >= len(self.filtered_sets):
            return

        set_data = self.filtered_sets[index]

        code = str(set_data.get("code", "")).strip()

        if not code:
            return

        query_parts = [f"set:{code}"]

        language = self.set_language_combo.get()

        if language != "any":
            query_parts.append(f"lang:{language}")

        query = " ".join(query_parts)

        self.start_search(
            query=query,
            page=1,
            unique="prints",
            order="set",
            direction="asc",
            include_extras=True,
        )

    # ======================================================
    # Результаты
    # ======================================================

    def _build_results_tab(self):
        top_row = ctk.CTkFrame(self.results_tab)
        top_row.pack(
            fill="x",
            padx=8,
            pady=8,
        )

        self.results_summary_label = ctk.CTkLabel(
            top_row,
            text="Поиск ещё не выполнялся",
            anchor="w",
        )
        self.results_summary_label.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
            pady=8,
        )

        self.previous_page_button = ctk.CTkButton(
            top_row,
            text="← Предыдущая",
            command=self.open_previous_page,
            width=130,
            state="disabled",
        )
        self.previous_page_button.pack(
            side="left",
            padx=4,
            pady=8,
        )

        self.next_page_button = ctk.CTkButton(
            top_row,
            text="Следующая →",
            command=self.open_next_page,
            width=130,
            state="disabled",
        )
        self.next_page_button.pack(
            side="left",
            padx=4,
            pady=8,
        )

        self.results_query_label = ctk.CTkLabel(
            self.results_tab,
            text="",
            anchor="w",
            justify="left",
            wraplength=1200,
        )
        self.results_query_label.pack(
            fill="x",
            padx=16,
            pady=(0, 6),
        )

        list_frame = ctk.CTkFrame(self.results_tab)
        list_frame.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8),
        )

        scrollbar = tk.Scrollbar(
            list_frame,
            orient="vertical",
        )
        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.results_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#1f1f1f",
            fg="#eeeeee",
            selectbackground="#1f6aa5",
            selectforeground="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 11),
            activestyle="none",
        )
        self.results_listbox.pack(
            side="left",
            fill="both",
            expand=True,
            padx=4,
            pady=4,
        )

        scrollbar.configure(command=self.results_listbox.yview)

        self.results_listbox.bind(
            "<Double-Button-1>",
            lambda event: (self.open_selected_result()),
        )

        self.results_listbox.bind(
            "<Return>",
            lambda event: (self.open_selected_result()),
        )

        bottom_row = ctk.CTkFrame(
            self.results_tab,
            fg_color="transparent",
        )
        bottom_row.pack(
            fill="x",
            padx=8,
            pady=(0, 8),
        )

        open_card_button = ctk.CTkButton(
            bottom_row,
            text="Открыть выбранную карту",
            command=self.open_selected_result,
            width=210,
        )
        open_card_button.pack(
            side="right",
        )

        self.results_status_label = ctk.CTkLabel(
            bottom_row,
            text="Готово",
            anchor="w",
        )
        self.results_status_label.pack(
            side="left",
            fill="x",
            expand=True,
        )

    def start_search(
        self,
        query,
        page=1,
        unique="cards",
        order="name",
        direction="auto",
        include_extras=False,
    ):
        query = str(query).strip()

        if not query:
            self._set_status("Поисковый запрос пустой")
            return

        if self.search_running:
            self._set_status("Дождитесь завершения текущего поиска")
            return

        self.search_running = True

        self.current_query = query
        self.current_page = max(
            1,
            int(page),
        )

        self.current_options = {
            "unique": unique,
            "order": order,
            "direction": direction,
            "include_extras": include_extras,
        }

        self._set_search_controls_state("disabled")

        self._set_status(f"Поиск: {query}")

        self.tabs.set(self.RESULTS_TAB)

        self.results_summary_label.configure(text="Загрузка результатов...")

        self.results_status_label.configure(text="Обращение к Scryfall...")

        self._run_background(
            self._search_worker,
            query,
            self.current_page,
            self.current_options,
        )

    def _search_worker(
        self,
        query,
        page,
        options,
    ):
        try:
            response = self.client.search_cards(
                query=query,
                page=page,
                unique=options["unique"],
                order=options["order"],
                direction=options["direction"],
                include_extras=options["include_extras"],
            )

            self.after(
                0,
                self._on_search_loaded,
                response,
                query,
                page,
                options,
            )

        except Exception as error:
            self.after(
                0,
                self._on_search_error,
                str(error),
            )

    def _on_search_loaded(
        self,
        response,
        query,
        page,
        options,
    ):
        self.search_running = False

        self.current_query = query
        self.current_page = page
        self.current_options = options

        self.result_cards = response.get(
            "data",
            [],
        )

        self.has_more_results = bool(
            response.get(
                "has_more",
                False,
            )
        )

        total_cards = int(
            response.get(
                "total_cards",
                len(self.result_cards),
            )
            or 0
        )

        self.results_listbox.delete(
            0,
            "end",
        )

        for card in self.result_cards:
            name = str(card.get("name", ""))

            set_code = str(card.get("set", "")).upper()

            rarity = str(card.get("rarity", ""))

            type_line = str(card.get("type_line", ""))

            line = f"{name:<48} " f"[{set_code:<6}] " f"{rarity:<10} " f"{type_line}"

            self.results_listbox.insert(
                "end",
                line,
            )

        self.results_summary_label.configure(
            text=(
                f"Найдено карт: {total_cards} | "
                f"Страница: {page} | "
                f"На странице: "
                f"{len(self.result_cards)}"
            )
        )

        self.results_query_label.configure(text=f"Запрос: {query}")

        self.previous_page_button.configure(
            state=("normal" if page > 1 else "disabled")
        )

        self.next_page_button.configure(
            state=("normal" if self.has_more_results else "disabled")
        )

        self._set_search_controls_state("normal")

        self._set_status(f"Поиск завершён. Найдено: {total_cards}")

        self.results_status_label.configure(
            text=("Выберите карту и нажмите Enter " "или дважды щёлкните по ней")
        )

        if len(self.result_cards) == 1:
            self.results_listbox.selection_set(0)
            self.open_selected_result()

    def _on_search_error(self, message):
        self.search_running = False

        self.result_cards = []
        self.has_more_results = False

        self.results_listbox.delete(
            0,
            "end",
        )

        self.results_summary_label.configure(text="Карты не найдены")

        self.results_status_label.configure(text=f"Ошибка поиска: {message}")

        self.previous_page_button.configure(state="disabled")
        self.next_page_button.configure(state="disabled")

        self._set_search_controls_state("normal")

        self._set_status(f"Ошибка поиска: {message}")

    def open_previous_page(self):
        if self.current_page <= 1:
            return

        self.start_search(
            query=self.current_query,
            page=self.current_page - 1,
            **self.current_options,
        )

    def open_next_page(self):
        if not self.has_more_results:
            return

        self.start_search(
            query=self.current_query,
            page=self.current_page + 1,
            **self.current_options,
        )

    def open_selected_result(self):
        selection = self.results_listbox.curselection()

        if not selection:
            self.results_status_label.configure(text="Выберите карту")
            return

        index = selection[0]

        if index >= len(self.result_cards):
            return

        card = self.result_cards[index]

        card_name = str(card.get("name", "")).strip()

        if not card_name:
            return

        self.results_status_label.configure(text=f"Открытие карты: {card_name}")

        self.search_callback(card_name)

    # ======================================================
    # Случайная карта
    # ======================================================

    def load_random_card(self):
        if self.search_running:
            return

        query = self.quick_query_entry.get().strip()

        self.search_running = True

        self._set_search_controls_state("disabled")

        self._set_status("Загрузка случайной карты...")

        self._run_background(
            self._random_card_worker,
            query,
        )

    def _random_card_worker(self, query):
        try:
            card = self.client.get_random_card(query=query or None)

            self.after(
                0,
                self._on_random_card_loaded,
                card,
                query,
            )

        except Exception as error:
            self.after(
                0,
                self._on_search_error,
                str(error),
            )

    def _on_random_card_loaded(
        self,
        card,
        query,
    ):
        self.search_running = False

        self._set_search_controls_state("normal")

        self.result_cards = [card]
        self.current_page = 1
        self.has_more_results = False

        card_name = str(card.get("name", ""))

        set_code = str(card.get("set", "")).upper()

        type_line = str(card.get("type_line", ""))

        self.results_listbox.delete(
            0,
            "end",
        )

        self.results_listbox.insert(
            "end",
            (f"{card_name:<48} " f"[{set_code:<6}] " f"{type_line}"),
        )

        self.results_listbox.selection_set(0)

        self.results_summary_label.configure(text="Случайная карта")

        self.results_query_label.configure(
            text=(f"Ограничение: {query}" if query else "Без ограничений")
        )

        self.previous_page_button.configure(state="disabled")
        self.next_page_button.configure(state="disabled")

        self.tabs.set(self.RESULTS_TAB)

        self._set_status(f"Случайная карта: {card_name}")

        if card_name:
            self.search_callback(card_name)

    # ======================================================
    # Общие методы
    # ======================================================

    def _entry_value(self, key):
        entry = self.advanced_entries.get(key)

        if entry is None:
            return ""

        return entry.get().strip()

    @staticmethod
    def _split_values(value):
        value = str(value).strip()

        if not value:
            return []

        normalized = value.replace(
            ";",
            ",",
        )

        return [item.strip() for item in normalized.split(",") if item.strip()]

    def _set_status(self, message):
        self.quick_status_label.configure(text=message)

        if hasattr(
            self,
            "results_status_label",
        ):
            self.results_status_label.configure(text=message)

    def _set_search_controls_state(
        self,
        state,
    ):
        self.quick_search_button.configure(state=state)

        self.random_card_button.configure(state=state)

        self.advanced_search_button.configure(state=state)

        if state == "disabled":
            self.previous_page_button.configure(state="disabled")
            self.next_page_button.configure(state="disabled")

    def _run_background(
        self,
        target,
        *args,
    ):
        thread = threading.Thread(
            target=target,
            args=args,
            daemon=True,
        )

        thread.start()
