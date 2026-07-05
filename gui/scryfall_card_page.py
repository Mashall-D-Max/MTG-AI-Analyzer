import hashlib
import threading
import webbrowser
from io import BytesIO
from pathlib import Path

import customtkinter as ctk
import requests
from PIL import Image, ImageOps

from gui.scryfall_card_preview import build_card_details
from utils.text_shortcuts import bind_text_shortcuts


class ScryfallCardPage(ctk.CTkFrame):
    """
    Встроенная страница конкретного издания карты.

    Используется как вкладка браузера внутри SearchPanel.
    """

    CACHE_DIRECTORY = Path("cache/scryfall_pages")
    IMAGE_SIZE = (390, 546)

    def __init__(
        self,
        master,
        card_data,
        on_back=None,
        on_close=None,
        on_add_to_deck=None,
    ):
        super().__init__(master)

        self.card_data = dict(card_data)
        self.on_back = on_back
        self.on_close = on_close
        self.on_add_to_deck = on_add_to_deck

        self.card_image = None
        self.image_request_active = True

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_content()

        self.after(50, self._start_image_loading)

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=(10, 5),
        )
        toolbar.grid_columnconfigure(1, weight=1)

        back_button = ctk.CTkButton(
            toolbar,
            text="← Результаты",
            command=self._go_back,
            width=130,
        )
        back_button.grid(
            row=0,
            column=0,
            padx=(10, 8),
            pady=10,
        )

        name = str(
            self.card_data.get("name", "Без названия")
        ).strip()
        set_code = str(
            self.card_data.get("set", "")
        ).upper().strip()
        collector_number = str(
            self.card_data.get("collector_number", "")
        ).strip()

        subtitle_parts = [name]

        if set_code:
            subtitle_parts.append(f"[{set_code}]")

        if collector_number:
            subtitle_parts.append(f"№ {collector_number}")

        title_label = ctk.CTkLabel(
            toolbar,
            text=" ".join(subtitle_parts),
            font=("Arial", 19, "bold"),
            anchor="w",
        )
        title_label.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=8,
            pady=10,
        )

        scryfall_uri = str(
            self.card_data.get("scryfall_uri", "")
        ).strip()

        open_web_button = ctk.CTkButton(
            toolbar,
            text="Открыть на Scryfall",
            command=self._open_on_scryfall,
            width=165,
            state=(
                "normal"
                if scryfall_uri
                else "disabled"
            ),
        )
        open_web_button.grid(
            row=0,
            column=2,
            padx=8,
            pady=10,
        )

        close_button = ctk.CTkButton(
            toolbar,
            text="Закрыть вкладку ×",
            command=self._close_page,
            width=150,
        )
        close_button.grid(
            row=0,
            column=3,
            padx=(8, 10),
            pady=10,
        )

    def _build_content(self):
        image_panel = ctk.CTkFrame(
            self,
            width=440,
        )
        image_panel.grid(
            row=1,
            column=0,
            sticky="ns",
            padx=(10, 5),
            pady=(5, 10),
        )
        image_panel.grid_propagate(False)
        image_panel.grid_columnconfigure(0, weight=1)
        image_panel.grid_rowconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(
            image_panel,
            text="Загрузка изображения...",
            justify="center",
        )
        self.image_label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=15,
            pady=15,
        )

        add_panel = ctk.CTkFrame(image_panel)
        add_panel.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 15),
        )
        add_panel.grid_columnconfigure(1, weight=1)

        quantity_label = ctk.CTkLabel(
            add_panel,
            text="Количество:",
            anchor="w",
        )
        quantity_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(10, 5),
        )

        self.quantity_entry = ctk.CTkEntry(
            add_panel,
            width=90,
        )
        self.quantity_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10,
            pady=(10, 5),
        )
        self.quantity_entry.insert(0, "1")
        bind_text_shortcuts(self.quantity_entry)

        zone_label = ctk.CTkLabel(
            add_panel,
            text="Зона:",
            anchor="w",
        )
        zone_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=10,
            pady=5,
        )

        self.zone_combo = ctk.CTkComboBox(
            add_panel,
            values=["Mainboard", "Sideboard"],
            state="readonly",
        )
        self.zone_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=5,
        )
        self.zone_combo.set("Mainboard")

        add_button = ctk.CTkButton(
            add_panel,
            text="Добавить в колоду",
            command=self._add_to_deck,
        )
        add_button.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=(8, 5),
        )

        self.add_status_label = ctk.CTkLabel(
            add_panel,
            text="",
            wraplength=360,
            justify="left",
            anchor="w",
        )
        self.add_status_label.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=(3, 10),
        )

        details_panel = ctk.CTkFrame(self)
        details_panel.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(5, 10),
            pady=(5, 10),
        )
        details_panel.grid_columnconfigure(0, weight=1)
        details_panel.grid_rowconfigure(1, weight=1)

        details_title = ctk.CTkLabel(
            details_panel,
            text="Информация о карте",
            font=("Arial", 20, "bold"),
            anchor="w",
        )
        details_title.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(15, 8),
        )

        self.details_textbox = ctk.CTkTextbox(
            details_panel,
            wrap="word",
            font=("Arial", 14),
        )
        self.details_textbox.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 15),
        )
        bind_text_shortcuts(self.details_textbox)
        self.details_textbox.insert(
            "1.0",
            build_card_details(self.card_data),
        )
        self.details_textbox.configure(state="disabled")

    def _add_to_deck(self):
        if self.on_add_to_deck is None:
            self.add_status_label.configure(
                text="Добавление в колоду недоступно"
            )
            return

        try:
            quantity = int(
                self.quantity_entry.get().strip()
            )
        except (TypeError, ValueError):
            self.add_status_label.configure(
                text="Количество должно быть целым числом"
            )
            return

        if quantity <= 0:
            self.add_status_label.configure(
                text="Количество должно быть больше нуля"
            )
            return

        zone = (
            "sideboard"
            if self.zone_combo.get() == "Sideboard"
            else "mainboard"
        )

        result = self.on_add_to_deck(
            self.card_data,
            quantity,
            zone,
        )

        if result is False:
            self.add_status_label.configure(
                text="Карта не была добавлена"
            )
            return

        zone_name = (
            "Sideboard"
            if zone == "sideboard"
            else "Mainboard"
        )
        self.add_status_label.configure(
            text=(
                f"Отправлено на добавление: "
                f"{quantity} × {self.card_data.get('name', '')} "
                f"в {zone_name}"
            )
        )

    def _go_back(self):
        if self.on_back is not None:
            self.on_back()

    def _close_page(self):
        if self.on_close is not None:
            self.on_close()

    def _open_on_scryfall(self):
        uri = str(
            self.card_data.get("scryfall_uri", "")
        ).strip()

        if uri:
            webbrowser.open(uri)

    def _start_image_loading(self):
        thread = threading.Thread(
            target=self._image_worker,
            daemon=True,
        )
        thread.start()

    def _image_worker(self):
        try:
            image = self._load_image()
        except Exception:
            image = None

        try:
            self.after(
                0,
                self._apply_image,
                image,
            )
        except Exception:
            return

    def _apply_image(self, image):
        if not self.image_request_active:
            return

        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        if image is None:
            self.image_label.configure(
                text="Изображение недоступно",
                image=None,
            )
            return

        self.card_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size,
        )
        self.image_label.configure(
            text="",
            image=self.card_image,
        )

    def _load_image(self):
        image_url = self._get_image_url()

        if not image_url:
            return None

        self.CACHE_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        cache_path = self._get_cache_path(
            image_url
        )

        image = self._read_cached_image(
            cache_path
        )

        if image is None:
            response = requests.get(
                image_url,
                headers={
                    "Accept": (
                        "image/avif,image/webp,"
                        "image/png,image/jpeg"
                    ),
                    "User-Agent": (
                        "MTG-AI-Analyzer/0.1 "
                        "(desktop deck analysis application)"
                    ),
                },
                timeout=25,
            )
            response.raise_for_status()

            with Image.open(
                BytesIO(response.content)
            ) as downloaded_image:
                image = ImageOps.exif_transpose(
                    downloaded_image
                ).convert("RGB")
                image.load()

            temporary_path = cache_path.with_name(
                cache_path.name + ".tmp"
            )
            image.save(
                temporary_path,
                format="PNG",
                optimize=True,
            )
            temporary_path.replace(cache_path)

        try:
            resampling = Image.Resampling.LANCZOS
        except AttributeError:
            resampling = Image.LANCZOS

        return ImageOps.contain(
            image=image,
            size=self.IMAGE_SIZE,
            method=resampling,
        )

    def _get_image_url(self):
        image_uris = self.card_data.get(
            "image_uris"
        )

        url = self._select_url(image_uris)

        if url:
            return url

        card_faces = self.card_data.get(
            "card_faces",
            [],
        )

        if not isinstance(card_faces, list):
            return None

        for face in card_faces:
            if not isinstance(face, dict):
                continue

            url = self._select_url(
                face.get("image_uris")
            )

            if url:
                return url

        return None

    @staticmethod
    def _select_url(image_uris):
        if not isinstance(image_uris, dict):
            return None

        for key in (
            "large",
            "normal",
            "png",
            "small",
        ):
            value = image_uris.get(key)

            if value:
                return str(value).strip()

        return None

    def _get_cache_path(self, image_url):
        card_id = str(
            self.card_data.get("id", "")
        ).strip()

        if card_id:
            key = card_id
        else:
            key = hashlib.sha256(
                image_url.encode(
                    "utf-8",
                    errors="ignore",
                )
            ).hexdigest()

        return self.CACHE_DIRECTORY / f"{key}.png"

    @staticmethod
    def _read_cached_image(cache_path):
        if not cache_path.exists():
            return None

        try:
            with Image.open(cache_path) as cached:
                image = ImageOps.exif_transpose(
                    cached
                ).convert("RGB")
                image.load()
                return image
        except (OSError, ValueError):
            try:
                cache_path.unlink()
            except OSError:
                pass
            return None

    def destroy(self):
        self.image_request_active = False
        super().destroy()
