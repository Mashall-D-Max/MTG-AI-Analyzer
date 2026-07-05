import customtkinter as ctk

from utils.text_shortcuts import bind_text_shortcuts


class DeckListPanel(ctk.CTkFrame):
    """
    Интерактивная панель mainboard и sideboard.

    Позволяет:
    - менять количество карты;
    - увеличивать и уменьшать количество;
    - переносить карту между зонами;
    - удалять строку из колоды.
    """

    def __init__(
        self,
        master,
        on_deck_changed=None,
    ):
        super().__init__(master)

        self.current_deck = None
        self.on_deck_changed = on_deck_changed
        self.quantity_entries = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title = ctk.CTkLabel(
            self,
            text="Редактор колоды",
            font=("Arial", 18, "bold"),
        )
        self.title.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 4),
        )

        self.summary_label = ctk.CTkLabel(
            self,
            text=(
                "Mainboard: 0 | "
                "Sideboard: 0 | "
                "Всего: 0"
            ),
        )
        self.summary_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 6),
        )

        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            width=650,
            height=500,
            fg_color="transparent",
        )
        self.cards_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )
        self.cards_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.empty_label = None

    # ======================================================
    # Публичные методы
    # ======================================================

    def show_deck(self, deck):
        self.current_deck = deck

        self.title.configure(
            text="Редактор колоды"
        )

        self.summary_label.configure(
            text=(
                f"Mainboard: {deck.mainboard_size} | "
                f"Sideboard: {deck.sideboard_size} | "
                f"Всего: {deck.total_size}"
            )
        )

        self._clear_rows()

        next_row = 0

        next_row = self._render_zone(
            title="Mainboard",
            zone_name="mainboard",
            cards=deck.cards,
            start_row=next_row,
        )

        self._render_zone(
            title="Sideboard",
            zone_name="sideboard",
            cards=deck.sideboard,
            start_row=next_row,
        )

    def show_error(self, message):
        self.current_deck = None
        self._clear_rows()

        self.title.configure(
            text="Редактор колоды"
        )

        self.summary_label.configure(
            text="Ошибка загрузки"
        )

        error_label = ctk.CTkLabel(
            self.cards_frame,
            text=(
                "Ошибка загрузки колоды\n\n"
                f"{message}"
            ),
            justify="left",
            anchor="nw",
            wraplength=600,
        )
        error_label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10,
        )

    def clear(self):
        self.current_deck = None
        self._clear_rows()

        self.summary_label.configure(
            text=(
                "Mainboard: 0 | "
                "Sideboard: 0 | "
                "Всего: 0"
            )
        )

        self.empty_label = ctk.CTkLabel(
            self.cards_frame,
            text="Колода не загружена",
        )
        self.empty_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=20,
        )

    # ======================================================
    # Отрисовка
    # ======================================================

    def _render_zone(
        self,
        title,
        zone_name,
        cards,
        start_row,
    ):
        section = ctk.CTkFrame(
            self.cards_frame
        )
        section.grid(
            row=start_row,
            column=0,
            sticky="ew",
            padx=2,
            pady=(2, 8),
        )
        section.grid_columnconfigure(
            0,
            weight=1,
        )

        header = ctk.CTkLabel(
            section,
            text=(
                f"{title} — "
                f"{sum(card.quantity for card in cards)}"
            ),
            font=("Arial", 16, "bold"),
            anchor="w",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(8, 5),
        )

        if not cards:
            empty_label = ctk.CTkLabel(
                section,
                text=f"{title} пуст",
                anchor="w",
                text_color=(
                    "#666666",
                    "#a0a0a0",
                ),
            )
            empty_label.grid(
                row=1,
                column=0,
                sticky="ew",
                padx=10,
                pady=(2, 10),
            )

            return start_row + 1

        for index, deck_card in enumerate(cards):
            self._render_card_row(
                parent=section,
                row=index + 1,
                zone_name=zone_name,
                index=index,
                deck_card=deck_card,
            )

        return start_row + 1

    def _render_card_row(
        self,
        parent,
        row,
        zone_name,
        index,
        deck_card,
    ):
        card_row = ctk.CTkFrame(
            parent,
            corner_radius=8,
        )
        card_row.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=8,
            pady=4,
        )

        card_row.grid_columnconfigure(
            0,
            weight=1,
        )

        info_frame = ctk.CTkFrame(
            card_row,
            fg_color="transparent",
        )
        info_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(8, 4),
            pady=7,
        )
        info_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        card_name = str(
            getattr(
                deck_card.card,
                "name",
                "Без названия",
            )
        ).strip()

        name_label = ctk.CTkLabel(
            info_frame,
            text=card_name,
            font=("Arial", 13, "bold"),
            anchor="w",
            justify="left",
            wraplength=280,
        )
        name_label.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        printing_label = str(
            getattr(
                deck_card,
                "printing_label",
                "",
            )
        ).strip()

        if printing_label:
            edition_label = ctk.CTkLabel(
                info_frame,
                text=printing_label,
                anchor="w",
                text_color=(
                    "#555555",
                    "#a8a8a8",
                ),
                font=("Arial", 11),
            )
            edition_label.grid(
                row=1,
                column=0,
                sticky="ew",
                pady=(2, 0),
            )

        controls = ctk.CTkFrame(
            card_row,
            fg_color="transparent",
        )
        controls.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(4, 8),
            pady=6,
        )

        minus_button = ctk.CTkButton(
            controls,
            text="−",
            width=34,
            command=lambda z=zone_name, i=index: (
                self._change_quantity(
                    zone_name=z,
                    index=i,
                    delta=-1,
                )
            ),
        )
        minus_button.pack(
            side="left",
            padx=2,
        )

        quantity_entry = ctk.CTkEntry(
            controls,
            width=52,
            justify="center",
        )
        quantity_entry.insert(
            0,
            str(deck_card.quantity),
        )
        quantity_entry.pack(
            side="left",
            padx=2,
        )
        bind_text_shortcuts(
            quantity_entry
        )

        quantity_entry.bind(
            "<Return>",
            lambda event, z=zone_name, i=index, e=quantity_entry: (
                self._apply_quantity(
                    zone_name=z,
                    index=i,
                    entry=e,
                )
            ),
        )

        self.quantity_entries.append(
            quantity_entry
        )

        apply_button = ctk.CTkButton(
            controls,
            text="✓",
            width=34,
            command=lambda z=zone_name, i=index, e=quantity_entry: (
                self._apply_quantity(
                    zone_name=z,
                    index=i,
                    entry=e,
                )
            ),
        )
        apply_button.pack(
            side="left",
            padx=2,
        )

        plus_button = ctk.CTkButton(
            controls,
            text="+",
            width=34,
            command=lambda z=zone_name, i=index: (
                self._change_quantity(
                    zone_name=z,
                    index=i,
                    delta=1,
                )
            ),
        )
        plus_button.pack(
            side="left",
            padx=2,
        )

        target_name = (
            "Sideboard"
            if zone_name == "mainboard"
            else "Mainboard"
        )

        move_button = ctk.CTkButton(
            controls,
            text=f"→ {target_name}",
            width=118,
            command=lambda z=zone_name, i=index: (
                self._move_card(
                    zone_name=z,
                    index=i,
                )
            ),
        )
        move_button.pack(
            side="left",
            padx=(6, 2),
        )

        delete_button = ctk.CTkButton(
            controls,
            text="Удалить",
            width=78,
            fg_color="#9b2c2c",
            hover_color="#7d2424",
            command=lambda z=zone_name, i=index: (
                self._remove_card(
                    zone_name=z,
                    index=i,
                )
            ),
        )
        delete_button.pack(
            side="left",
            padx=(6, 2),
        )

    def _clear_rows(self):
        self.quantity_entries = []
        self.empty_label = None

        for child in self.cards_frame.winfo_children():
            child.destroy()

    # ======================================================
    # Действия редактирования
    # ======================================================

    def _apply_quantity(
        self,
        zone_name,
        index,
        entry,
    ):
        if self.current_deck is None:
            return

        value = entry.get().strip()

        try:
            quantity = int(value)
        except ValueError:
            self._notify_error(
                "Количество должно быть целым числом"
            )
            return

        if quantity < 0:
            self._notify_error(
                "Количество не может быть отрицательным"
            )
            return

        try:
            zone = self.current_deck.get_zone(
                zone_name
            )
            card_name = zone[index].name

            result = self.current_deck.set_quantity(
                zone=zone_name,
                index=index,
                quantity=quantity,
            )

            if result is None:
                message = (
                    f"{card_name} удалена из "
                    f"{self._visible_zone_name(zone_name)}"
                )
            else:
                message = (
                    f"Количество {card_name}: "
                    f"{result.quantity}"
                )

            self._finish_change(message)

        except Exception as error:
            self._notify_error(str(error))

    def _change_quantity(
        self,
        zone_name,
        index,
        delta,
    ):
        if self.current_deck is None:
            return

        try:
            zone = self.current_deck.get_zone(
                zone_name
            )
            card_name = zone[index].name

            result = self.current_deck.change_quantity(
                zone=zone_name,
                index=index,
                delta=delta,
            )

            if result is None:
                message = (
                    f"{card_name} удалена из "
                    f"{self._visible_zone_name(zone_name)}"
                )
            else:
                message = (
                    f"Количество {card_name}: "
                    f"{result.quantity}"
                )

            self._finish_change(message)

        except Exception as error:
            self._notify_error(str(error))

    def _move_card(
        self,
        zone_name,
        index,
    ):
        if self.current_deck is None:
            return

        try:
            source_zone = self.current_deck.get_zone(
                zone_name
            )
            card_name = source_zone[index].name

            target_zone = (
                "sideboard"
                if zone_name == "mainboard"
                else "mainboard"
            )

            moved_card = self.current_deck.move_card(
                source_zone=zone_name,
                index=index,
                target_zone=target_zone,
            )

            message = (
                f"{card_name} перенесена в "
                f"{self._visible_zone_name(target_zone)}. "
                f"Количество в зоне: {moved_card.quantity}"
            )

            self._finish_change(message)

        except Exception as error:
            self._notify_error(str(error))

    def _remove_card(
        self,
        zone_name,
        index,
    ):
        if self.current_deck is None:
            return

        try:
            removed_card = self.current_deck.remove_at(
                zone=zone_name,
                index=index,
            )

            message = (
                f"{removed_card.name} удалена из "
                f"{self._visible_zone_name(zone_name)}"
            )

            self._finish_change(message)

        except Exception as error:
            self._notify_error(str(error))

    def _finish_change(self, message):
        self.show_deck(self.current_deck)

        if self.on_deck_changed is not None:
            self.on_deck_changed(
                self.current_deck,
                message,
            )

    def _notify_error(self, message):
        if self.on_deck_changed is not None:
            self.on_deck_changed(
                self.current_deck,
                f"Ошибка редактирования: {message}",
                is_error=True,
            )

    @staticmethod
    def _visible_zone_name(zone_name):
        if zone_name == "sideboard":
            return "Sideboard"

        return "Mainboard"
