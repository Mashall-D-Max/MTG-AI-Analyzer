import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from services.saved_deck_library import (
    SavedDeckLibraryService,
)
from utils.text_shortcuts import bind_text_shortcuts


class SavedDecksPanel(ctk.CTkFrame):
    """
    Вкладка внутренней библиотеки сохранённых колод.
    """

    def __init__(
        self,
        master,
        on_open_deck,
    ):
        super().__init__(master)

        self.on_open_deck = on_open_deck
        self.all_entries = []
        self.visible_entries = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_actions()

        self.after(50, self.refresh)

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(12, 5),
        )

        title = ctk.CTkLabel(
            header,
            text="Сохранённые колоды",
            font=("Arial", 22, "bold"),
            anchor="w",
        )
        title.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.count_label = ctk.CTkLabel(
            header,
            text="Колоды: 0",
        )
        self.count_label.pack(
            side="right",
            padx=(10, 0),
        )

    def _build_filters(self):
        filters = ctk.CTkFrame(self)
        filters.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=5,
        )
        filters.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filters,
            placeholder_text=(
                "Поиск по названию, формату или типу файла..."
            ),
        )
        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(10, 6),
            pady=10,
        )
        bind_text_shortcuts(self.search_entry)
        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.apply_filter(),
            add="+",
        )

        refresh_button = ctk.CTkButton(
            filters,
            text="Обновить",
            command=self.refresh,
            width=120,
        )
        refresh_button.grid(
            row=0,
            column=1,
            padx=(6, 10),
            pady=10,
        )

    def _build_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=5,
        )
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "SavedDecks.Treeview",
            background="#202020",
            fieldbackground="#202020",
            foreground="#eeeeee",
            rowheight=30,
            borderwidth=0,
            font=("Arial", 11),
        )
        style.configure(
            "SavedDecks.Treeview.Heading",
            background="#303030",
            foreground="#ffffff",
            relief="flat",
            font=("Arial", 11, "bold"),
        )
        style.map(
            "SavedDecks.Treeview",
            background=[("selected", "#1f6aa5")],
            foreground=[("selected", "#ffffff")],
        )

        columns = (
            "deck_name",
            "game_format",
            "export_format",
            "modified",
            "size",
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="SavedDecks.Treeview",
            selectmode="browse",
        )

        self.tree.heading(
            "deck_name",
            text="Наименование",
        )
        self.tree.heading(
            "game_format",
            text="Игровой формат",
        )
        self.tree.heading(
            "export_format",
            text="Формат файла",
        )
        self.tree.heading(
            "modified",
            text="Изменён",
        )
        self.tree.heading(
            "size",
            text="Размер",
        )

        self.tree.column(
            "deck_name",
            width=320,
            minwidth=180,
            anchor="w",
        )
        self.tree.column(
            "game_format",
            width=170,
            minwidth=120,
            anchor="w",
        )
        self.tree.column(
            "export_format",
            width=210,
            minwidth=150,
            anchor="w",
        )
        self.tree.column(
            "modified",
            width=160,
            minwidth=140,
            anchor="center",
        )
        self.tree.column(
            "size",
            width=90,
            minwidth=80,
            anchor="e",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(8, 0),
            pady=(8, 0),
        )
        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            pady=(8, 0),
        )
        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(8, 0),
            pady=(0, 8),
        )

        self.tree.bind(
            "<Double-Button-1>",
            lambda event: self.open_selected(),
        )
        self.tree.bind(
            "<Return>",
            lambda event: self.open_selected(),
        )
        self.tree.bind(
            "<<TreeviewSelect>>",
            lambda event: self._update_selection_status(),
        )

    def _build_actions(self):
        actions = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        actions.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=12,
            pady=(5, 12),
        )

        self.status_label = ctk.CTkLabel(
            actions,
            text="Библиотека ещё не загружена",
            anchor="w",
        )
        self.status_label.pack(
            side="left",
            fill="x",
            expand=True,
        )

        open_button = ctk.CTkButton(
            actions,
            text="Открыть в анализе",
            command=self.open_selected,
            width=170,
        )
        open_button.pack(
            side="right",
            padx=(8, 0),
        )

        folder_button = ctk.CTkButton(
            actions,
            text="Открыть папку",
            command=self.open_selected_folder,
            width=145,
        )
        folder_button.pack(
            side="right",
            padx=8,
        )

        delete_button = ctk.CTkButton(
            actions,
            text="Удалить",
            command=self.delete_selected,
            width=110,
            fg_color="#9b2c2c",
            hover_color="#7f1d1d",
        )
        delete_button.pack(
            side="right",
            padx=8,
        )

    def refresh(self):
        try:
            self.all_entries = (
                SavedDeckLibraryService.scan()
            )
            self.apply_filter()
        except Exception as error:
            self.all_entries = []
            self.visible_entries = []
            self._render_entries()
            self.status_label.configure(
                text=f"Ошибка загрузки библиотеки: {error}"
            )

    def apply_filter(self):
        search_text = (
            self.search_entry.get().strip().casefold()
        )

        if not search_text:
            self.visible_entries = list(
                self.all_entries
            )
        else:
            self.visible_entries = [
                entry
                for entry in self.all_entries
                if search_text
                in " ".join(
                    (
                        entry.deck_name,
                        entry.game_format,
                        entry.export_format_label,
                        str(entry.path),
                    )
                ).casefold()
            ]

        self._render_entries()

    def _render_entries(self):
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        for index, entry in enumerate(
            self.visible_entries
        ):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    entry.deck_name,
                    entry.game_format,
                    entry.export_format_label,
                    entry.modified_text,
                    entry.size_text,
                ),
            )

        self.count_label.configure(
            text=(
                f"Колоды: {len(self.visible_entries)}"
                f" из {len(self.all_entries)}"
            )
        )

        if self.visible_entries:
            self.status_label.configure(
                text=(
                    "Дважды нажмите на колоду, "
                    "чтобы открыть её в анализе"
                )
            )
        else:
            self.status_label.configure(
                text=(
                    "Сохранённых колод не найдено. "
                    "Используйте кнопку «Сохранить колоду»."
                )
            )

    def get_selected_entry(self):
        selection = self.tree.selection()

        if not selection:
            return None

        try:
            index = int(selection[0])
        except (TypeError, ValueError):
            return None

        if index < 0 or index >= len(
            self.visible_entries
        ):
            return None

        return self.visible_entries[index]

    def open_selected(self):
        entry = self.get_selected_entry()

        if entry is None:
            self.status_label.configure(
                text="Выберите сохранённую колоду"
            )
            return

        self.status_label.configure(
            text=f"Открытие колоды: {entry.deck_name}"
        )

        if self.on_open_deck is not None:
            self.on_open_deck(entry)

    def delete_selected(self):
        entry = self.get_selected_entry()

        if entry is None:
            self.status_label.configure(
                text="Выберите колоду для удаления"
            )
            return

        confirmed = messagebox.askyesno(
            title="Удаление колоды",
            message=(
                f"Удалить сохранённую колоду "
                f"«{entry.deck_name}»?\n\n"
                f"{entry.path}"
            ),
            parent=self.winfo_toplevel(),
        )

        if not confirmed:
            return

        try:
            SavedDeckLibraryService.delete(entry)
            self.refresh()
            self.status_label.configure(
                text=f"Колода удалена: {entry.deck_name}"
            )
        except Exception as error:
            self.status_label.configure(
                text=f"Ошибка удаления: {error}"
            )

    def open_selected_folder(self):
        entry = self.get_selected_entry()

        if entry is None:
            self.status_label.configure(
                text="Выберите сохранённую колоду"
            )
            return

        directory = entry.path.parent

        try:
            if sys.platform.startswith("win"):
                os.startfile(directory)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(directory)])
            else:
                subprocess.Popen(["xdg-open", str(directory)])
        except Exception as error:
            self.status_label.configure(
                text=f"Не удалось открыть папку: {error}"
            )

    def _update_selection_status(self):
        entry = self.get_selected_entry()

        if entry is None:
            return

        self.status_label.configure(
            text=(
                f"Выбрано: {entry.deck_name} | "
                f"{entry.game_format} | "
                f"{entry.export_format_label}"
            )
        )
