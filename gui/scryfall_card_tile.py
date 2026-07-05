import customtkinter as ctk

from gui.scryfall_card_preview import (
    ScryfallCardPreview,
)


class ScryfallCardTile(ctk.CTkFrame):
    """
    Визуальная карточка результата поиска Scryfall.

    Один щелчок выбирает карту.
    Двойной щелчок открывает подробный просмотр.
    """

    NORMAL_BORDER_COLOR = (
        "#b5b5b5",
        "#3a3a3a",
    )

    SELECTED_BORDER_COLOR = (
        "#1f6aa5",
        "#3b8ed0",
    )

    def __init__(
        self,
        master,
        card_data,
        index,
        on_select,
        on_open,
        on_add_to_deck=None,
        width=190,
        height=330,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=10,
            border_width=2,
            border_color=(
                self.NORMAL_BORDER_COLOR
            ),
        )

        self.card_data = card_data
        self.index = index
        self.on_select = on_select
        self.on_open = on_open
        self.on_add_to_deck = on_add_to_deck

        self.card_image = None
        self.is_selected = False
        self.preview_window = None

        self.grid_propagate(False)
        self.grid_columnconfigure(
            0,
            weight=1,
        )
        self.grid_rowconfigure(
            0,
            weight=1,
        )

        self.image_frame = ctk.CTkFrame(
            self,
            width=174,
            height=244,
            corner_radius=8,
        )
        self.image_frame.grid(
            row=0,
            column=0,
            padx=7,
            pady=(7, 4),
            sticky="nsew",
        )
        self.image_frame.grid_propagate(
            False
        )

        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text=(
                "Загрузка\n"
                "изображения..."
            ),
            justify="center",
        )
        self.image_label.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3,
        )

        card_name = str(
            card_data.get(
                "name",
                "",
            )
        ).strip()

        if not card_name:
            card_name = "Без названия"

        self.name_label = ctk.CTkLabel(
            self,
            text=card_name,
            font=(
                "Arial",
                13,
                "bold",
            ),
            justify="center",
            wraplength=172,
        )
        self.name_label.grid(
            row=1,
            column=0,
            padx=7,
            pady=(3, 2),
            sticky="ew",
        )

        set_code = str(
            card_data.get(
                "set",
                "",
            )
        ).upper()

        rarity = str(
            card_data.get(
                "rarity",
                "",
            )
        ).capitalize()

        collector_number = str(
            card_data.get(
                "collector_number",
                "",
            )
        )

        details = []

        if set_code:
            details.append(set_code)

        if collector_number:
            details.append(
                f"№ {collector_number}"
            )

        if rarity:
            details.append(rarity)

        self.details_label = ctk.CTkLabel(
            self,
            text=" · ".join(details),
            font=(
                "Arial",
                11,
            ),
            text_color=(
                "#555555",
                "#b0b0b0",
            ),
            justify="center",
            wraplength=172,
        )
        self.details_label.grid(
            row=2,
            column=0,
            padx=7,
            pady=(0, 7),
            sticky="ew",
        )

        self._bind_mouse_events()

    def set_image(self, pil_image):
        if pil_image is None:
            self.show_image_error()
            return

        image_width, image_height = (
            pil_image.size
        )

        self.card_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(
                image_width,
                image_height,
            ),
        )

        self.image_label.configure(
            image=self.card_image,
            text="",
        )

    def show_image_error(self):
        self.card_image = None

        self.image_label.configure(
            image=None,
            text=(
                "Изображение\n"
                "недоступно"
            ),
        )

    def set_selected(self, selected):
        self.is_selected = bool(selected)

        self.configure(
            border_color=(
                self.SELECTED_BORDER_COLOR
                if self.is_selected
                else self.NORMAL_BORDER_COLOR
            )
        )

    def _bind_mouse_events(self):
        widgets = (
            self,
            self.image_frame,
            self.image_label,
            self.name_label,
            self.details_label,
        )

        for widget in widgets:
            widget.bind(
                "<Button-1>",
                self._handle_select,
                add="+",
            )
            widget.bind(
                "<Double-Button-1>",
                self._handle_preview,
                add="+",
            )

    def _handle_select(self, event=None):
        if self.on_select is not None:
            self.on_select(self.index)

    def _handle_preview(self, event=None):
        if self.on_select is not None:
            self.on_select(self.index)

        if (
            self.preview_window is not None
            and self.preview_window.winfo_exists()
        ):
            self.preview_window.focus_force()
            self.preview_window.lift()
            return "break"

        self.preview_window = ScryfallCardPreview(
            master=self,
            card_data=self.card_data,
            on_open_in_analyzer=(
                self._open_in_analyzer
            ),
            on_add_to_deck=(
                self.on_add_to_deck
            ),
        )

        return "break"

    def _open_in_analyzer(self):
        if self.on_open is not None:
            self.on_open(self.index)
