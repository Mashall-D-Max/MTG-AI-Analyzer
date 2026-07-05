import hashlib
import threading
import webbrowser
from io import BytesIO
from pathlib import Path

import customtkinter as ctk
import requests

from PIL import Image, ImageOps

from utils.text_shortcuts import bind_text_shortcuts

LEGALITY_NAMES = {
    "standard": "Standard",
    "future": "Future",
    "historic": "Historic",
    "timeless": "Timeless",
    "gladiator": "Gladiator",
    "pioneer": "Pioneer",
    "explorer": "Explorer",
    "modern": "Modern",
    "legacy": "Legacy",
    "pauper": "Pauper",
    "vintage": "Vintage",
    "penny": "Penny",
    "commander": "Commander",
    "oathbreaker": "Oathbreaker",
    "standardbrawl": "Standard Brawl",
    "brawl": "Brawl",
    "alchemy": "Alchemy",
    "paupercommander": "Pauper Commander",
    "duel": "Duel Commander",
    "oldschool": "Old School",
    "premodern": "Premodern",
    "predh": "PreDH",
}


LEGALITY_STATUSES = {
    "legal": "легальна",
    "not_legal": "нелегальна",
    "banned": "запрещена",
    "restricted": "ограничена",
}


def build_card_details(card_data):
    """
    Формирует текстовое описание карты
    из исходного JSON Scryfall.
    """

    if not isinstance(card_data, dict):
        return "Некорректные данные карты."

    lines = []

    name = str(
        card_data.get(
            "name",
            "Без названия",
        )
    ).strip()

    lines.append(name)
    lines.append("=" * max(30, len(name)))
    lines.append("")

    card_faces = card_data.get(
        "card_faces",
        [],
    )

    if isinstance(card_faces, list) and card_faces:
        for index, face in enumerate(
            card_faces,
            start=1,
        ):
            if not isinstance(face, dict):
                continue

            face_name = str(
                face.get(
                    "name",
                    f"Сторона {index}",
                )
            ).strip()

            lines.append(f"=== {face_name} ===")

            _append_card_characteristics(
                lines=lines,
                card_data=face,
            )

            lines.append("")
    else:
        _append_card_characteristics(
            lines=lines,
            card_data=card_data,
        )

        lines.append("")

    set_name = str(
        card_data.get(
            "set_name",
            "",
        )
    ).strip()

    set_code = (
        str(
            card_data.get(
                "set",
                "",
            )
        )
        .upper()
        .strip()
    )

    collector_number = str(
        card_data.get(
            "collector_number",
            "",
        )
    ).strip()

    set_parts = []

    if set_name:
        set_parts.append(set_name)

    if set_code:
        set_parts.append(f"[{set_code}]")

    if collector_number:
        set_parts.append(f"№ {collector_number}")

    if set_parts:
        lines.append("Набор: " + " ".join(set_parts))

    released_at = str(
        card_data.get(
            "released_at",
            "",
        )
    ).strip()

    if released_at:
        lines.append(f"Дата выпуска: {released_at}")

    rarity = str(
        card_data.get(
            "rarity",
            "",
        )
    ).strip()

    if rarity:
        lines.append(f"Редкость: {rarity.capitalize()}")

    language = str(
        card_data.get(
            "lang",
            "",
        )
    ).strip()

    if language:
        lines.append(f"Язык: {language}")

    artist = str(
        card_data.get(
            "artist",
            "",
        )
    ).strip()

    if artist:
        lines.append(f"Художник: {artist}")

    games = card_data.get(
        "games",
        [],
    )

    if isinstance(games, list) and games:
        lines.append("Доступна в: " + ", ".join(str(game) for game in games))

    finishes = card_data.get(
        "finishes",
        [],
    )

    if isinstance(finishes, list) and finishes:
        lines.append(
            "Варианты печати: " + ", ".join(str(finish) for finish in finishes)
        )

    prices = card_data.get(
        "prices",
        {},
    )

    if isinstance(prices, dict):
        price_lines = _build_price_lines(prices)

        if price_lines:
            lines.append("")
            lines.append("=== Цены ===")
            lines.extend(price_lines)

    legalities = card_data.get(
        "legalities",
        {},
    )

    if isinstance(legalities, dict):
        legality_lines = _build_legality_lines(legalities)

        if legality_lines:
            lines.append("")
            lines.append("=== Легальность ===")
            lines.extend(legality_lines)

    reserved = card_data.get("reserved")

    if reserved:
        lines.append("")
        lines.append("Карта находится в Reserved List.")

    promo_types = card_data.get(
        "promo_types",
        [],
    )

    if isinstance(promo_types, list) and promo_types:
        lines.append("")
        lines.append("Промо-типы: " + ", ".join(str(item) for item in promo_types))

    return "\n".join(lines).strip()


def _append_card_characteristics(
    lines,
    card_data,
):
    mana_cost = str(
        card_data.get(
            "mana_cost",
            "",
        )
    ).strip()

    if mana_cost:
        lines.append(f"Мана: {mana_cost}")

    type_line = str(
        card_data.get(
            "type_line",
            "",
        )
    ).strip()

    if type_line:
        lines.append(f"Тип: {type_line}")

    oracle_text = str(
        card_data.get(
            "oracle_text",
            "",
        )
    ).strip()

    if oracle_text:
        lines.append("")
        lines.append("Oracle-текст:")
        lines.append(oracle_text)

    power = card_data.get("power")

    toughness = card_data.get("toughness")

    if power is not None and toughness is not None:
        lines.append("")
        lines.append(f"Сила / выносливость: " f"{power} / {toughness}")

    loyalty = card_data.get("loyalty")

    if loyalty is not None:
        lines.append("")
        lines.append(f"Лояльность: {loyalty}")

    defense = card_data.get("defense")

    if defense is not None:
        lines.append("")
        lines.append(f"Защита: {defense}")


def _build_price_lines(prices):
    labels = {
        "usd": "USD",
        "usd_foil": "USD foil",
        "usd_etched": "USD etched",
        "eur": "EUR",
        "eur_foil": "EUR foil",
        "tix": "MTGO TIX",
    }

    result = []

    for key, label in labels.items():
        value = prices.get(key)

        if value in (
            None,
            "",
        ):
            continue

        result.append(f"{label}: {value}")

    return result


def _build_legality_lines(legalities):
    result = []

    for format_name, status in legalities.items():
        if status == "not_legal":
            continue

        visible_name = LEGALITY_NAMES.get(
            format_name,
            format_name.replace(
                "_",
                " ",
            ).title(),
        )

        visible_status = LEGALITY_STATUSES.get(
            status,
            status,
        )

        result.append(f"{visible_name}: {visible_status}")

    return result


class ScryfallCardPreview(ctk.CTkToplevel):
    """
    Окно подробного просмотра конкретного
    издания карты Scryfall.
    """

    CACHE_DIRECTORY = Path("cache/scryfall_previews")

    IMAGE_SIZE = (
        360,
        504,
    )

    _cache_lock = threading.Lock()

    def __init__(
        self,
        master,
        card_data,
        on_open_in_analyzer=None,
    ):
        super().__init__(master)

        self.card_data = card_data
        self.on_open_in_analyzer = on_open_in_analyzer

        self.preview_image = None
        self.image_thread = None

        card_name = str(
            card_data.get(
                "name",
                "Просмотр карты",
            )
        )

        self.title(card_name)
        self.geometry("1080x720")
        self.minsize(900, 620)

        self.transient(master.winfo_toplevel())

        self.protocol(
            "WM_DELETE_WINDOW",
            self.destroy,
        )

        self.grid_columnconfigure(
            0,
            weight=0,
        )

        self.grid_columnconfigure(
            1,
            weight=1,
        )

        self.grid_rowconfigure(
            0,
            weight=1,
        )

        self._build_image_panel()
        self._build_information_panel()

        self.after(
            50,
            self._start_image_loading,
        )

        self.focus_force()

    # ======================================================
    # Интерфейс
    # ======================================================

    def _build_image_panel(self):
        image_panel = ctk.CTkFrame(
            self,
            width=410,
        )
        image_panel.grid(
            row=0,
            column=0,
            sticky="ns",
            padx=(15, 8),
            pady=15,
        )

        image_panel.grid_propagate(False)

        image_panel.grid_rowconfigure(
            0,
            weight=1,
        )

        image_panel.grid_columnconfigure(
            0,
            weight=1,
        )

        self.image_label = ctk.CTkLabel(
            image_panel,
            text=("Загрузка крупного\n" "изображения..."),
            justify="center",
        )
        self.image_label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=15,
            pady=15,
        )

    def _build_information_panel(self):
        information_panel = ctk.CTkFrame(self)
        information_panel.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 15),
            pady=15,
        )

        information_panel.grid_columnconfigure(
            0,
            weight=1,
        )

        information_panel.grid_rowconfigure(
            1,
            weight=1,
        )

        card_name = str(
            self.card_data.get(
                "name",
                "Без названия",
            )
        )

        title_label = ctk.CTkLabel(
            information_panel,
            text=card_name,
            font=(
                "Arial",
                24,
                "bold",
            ),
            justify="left",
            anchor="w",
            wraplength=560,
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(15, 8),
        )

        self.details_textbox = ctk.CTkTextbox(
            information_panel,
            wrap="word",
            font=(
                "Arial",
                14,
            ),
        )
        self.details_textbox.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=8,
        )

        bind_text_shortcuts(self.details_textbox)

        self.details_textbox.insert(
            "1.0",
            build_card_details(self.card_data),
        )

        self.details_textbox.configure(state="disabled")

        buttons_panel = ctk.CTkFrame(
            information_panel,
            fg_color="transparent",
        )
        buttons_panel.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=15,
            pady=(8, 15),
        )

        if self.on_open_in_analyzer is not None:
            open_analyzer_button = ctk.CTkButton(
                buttons_panel,
                text="Открыть в анализе",
                command=(self._open_in_analyzer),
                width=170,
            )
            open_analyzer_button.pack(
                side="left",
                padx=(0, 8),
            )

        scryfall_uri = str(
            self.card_data.get(
                "scryfall_uri",
                "",
            )
        ).strip()

        self.open_scryfall_button = ctk.CTkButton(
            buttons_panel,
            text="Открыть на Scryfall",
            command=(self._open_on_scryfall),
            width=180,
            state=("normal" if scryfall_uri else "disabled"),
        )
        self.open_scryfall_button.pack(
            side="left",
            padx=8,
        )

        close_button = ctk.CTkButton(
            buttons_panel,
            text="Закрыть",
            command=self.destroy,
            width=120,
        )
        close_button.pack(
            side="right",
            padx=(8, 0),
        )

    # ======================================================
    # Действия
    # ======================================================

    def _open_in_analyzer(self):
        if self.on_open_in_analyzer is None:
            return

        self.on_open_in_analyzer()

        self.destroy()

    def _open_on_scryfall(self):
        scryfall_uri = str(
            self.card_data.get(
                "scryfall_uri",
                "",
            )
        ).strip()

        if not scryfall_uri:
            return

        webbrowser.open(scryfall_uri)

    # ======================================================
    # Изображение
    # ======================================================

    def _start_image_loading(self):
        self.image_thread = threading.Thread(
            target=self._image_worker,
            daemon=True,
        )

        self.image_thread.start()

    def _image_worker(self):
        try:
            image = self._load_preview_image()

        except Exception:
            image = None

        try:
            self.after(
                0,
                self._apply_preview_image,
                image,
            )
        except Exception:
            return

    def _apply_preview_image(
        self,
        image,
    ):
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        if image is None:
            self.image_label.configure(
                image=None,
                text=("Крупное изображение\n" "недоступно"),
            )
            return

        image_width, image_height = image.size

        self.preview_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(
                image_width,
                image_height,
            ),
        )

        self.image_label.configure(
            image=self.preview_image,
            text="",
        )

    def _load_preview_image(self):
        image_url = self._get_preview_image_url()

        if not image_url:
            return None

        self.CACHE_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        cache_path = self._get_cache_path(image_url)

        image = self._load_cached_image(cache_path)

        if image is None:
            image = self._download_image(image_url)

            self._save_cached_image(
                image=image,
                cache_path=cache_path,
            )

        return self._resize_image(image)

    def _get_preview_image_url(self):
        image_uris = self.card_data.get("image_uris")

        image_url = self._select_image_url(image_uris)

        if image_url:
            return image_url

        card_faces = self.card_data.get(
            "card_faces",
            [],
        )

        if not isinstance(
            card_faces,
            list,
        ):
            return None

        for face in card_faces:
            if not isinstance(
                face,
                dict,
            ):
                continue

            image_url = self._select_image_url(face.get("image_uris"))

            if image_url:
                return image_url

        return None

    @staticmethod
    def _select_image_url(
        image_uris,
    ):
        if not isinstance(
            image_uris,
            dict,
        ):
            return None

        for image_size in (
            "large",
            "normal",
            "png",
            "small",
        ):
            image_url = image_uris.get(image_size)

            if image_url:
                return str(image_url).strip()

        return None

    def _get_cache_path(
        self,
        image_url,
    ):
        card_id = str(
            self.card_data.get(
                "id",
                "",
            )
        ).strip()

        if card_id:
            cache_name = card_id
        else:
            cache_name = hashlib.sha256(
                image_url.encode(
                    "utf-8",
                    errors="ignore",
                )
            ).hexdigest()

        return self.CACHE_DIRECTORY / f"{cache_name}.png"

    @staticmethod
    def _load_cached_image(
        cache_path,
    ):
        if not cache_path.exists():
            return None

        try:
            with Image.open(cache_path) as cached_image:
                image = ImageOps.exif_transpose(cached_image).convert("RGB")

                image.load()

                return image

        except (
            OSError,
            ValueError,
        ):
            try:
                cache_path.unlink()
            except OSError:
                pass

            return None

    def _download_image(
        self,
        image_url,
    ):
        response = requests.get(
            image_url,
            headers={
                "Accept": ("image/avif," "image/webp," "image/png," "image/jpeg"),
                "User-Agent": (
                    "MTG-AI-Analyzer/0.1 " "(desktop deck analysis application)"
                ),
            },
            timeout=25,
        )

        response.raise_for_status()

        with Image.open(BytesIO(response.content)) as downloaded_image:
            image = ImageOps.exif_transpose(downloaded_image).convert("RGB")

            image.load()

            return image

    def _save_cached_image(
        self,
        image,
        cache_path,
    ):
        temporary_path = cache_path.with_name(cache_path.name + ".tmp")

        with self._cache_lock:
            if cache_path.exists():
                return

            try:
                image.save(
                    temporary_path,
                    format="PNG",
                    optimize=True,
                )

                temporary_path.replace(cache_path)

            finally:
                if temporary_path.exists():
                    try:
                        temporary_path.unlink()
                    except OSError:
                        pass

    def _resize_image(
        self,
        image,
    ):
        try:
            resampling = Image.Resampling.LANCZOS
        except AttributeError:
            resampling = Image.LANCZOS

        return ImageOps.contain(
            image=image,
            size=self.IMAGE_SIZE,
            method=resampling,
        )
