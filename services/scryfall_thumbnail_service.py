import hashlib
import re
import threading
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageOps


class ScryfallThumbnailError(RuntimeError):
    """
    Ошибка загрузки или обработки изображения Scryfall.
    """


class ScryfallThumbnailService:
    """
    Сервис загрузки и локального кэширования
    миниатюр карт Scryfall.
    """

    DEFAULT_CACHE_DIRECTORY = "cache/scryfall_thumbnails"

    def __init__(
        self,
        cache_directory=None,
        session=None,
        timeout=20,
    ):
        if cache_directory is None:
            cache_directory = self.DEFAULT_CACHE_DIRECTORY

        self.cache_directory = Path(cache_directory)

        self.cache_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.session = session if session is not None else requests.Session()

        self.timeout = timeout

        self.headers = {
            "Accept": ("image/avif," "image/webp," "image/png," "image/jpeg"),
            "User-Agent": (
                "MTG-AI-Analyzer/0.1 " "(desktop deck analysis application)"
            ),
        }

        self._cache_lock = threading.Lock()

    # ======================================================
    # Public API
    # ======================================================

    def load_thumbnail(
        self,
        card_data,
        size=(180, 252),
    ):
        """
        Загружает изображение карты и возвращает
        уменьшенный объект PIL.Image.

        При повторном запросе изображение берётся
        из локального кэша.
        """

        if not isinstance(card_data, dict):
            raise TypeError("Данные карты должны быть словарём")

        image_url = self.get_image_url(card_data)

        if not image_url:
            raise ScryfallThumbnailError("У карты отсутствует изображение")

        cache_path = self.get_cache_path(
            card_data=card_data,
            image_url=image_url,
        )

        image = self._load_from_cache(cache_path)

        if image is None:
            image = self._download_image(image_url)

            self._save_to_cache(
                image=image,
                cache_path=cache_path,
            )

        return self._resize_image(
            image=image,
            size=size,
        )

    def get_image_url(
        self,
        card_data,
    ):
        """
        Возвращает URL изображения карты.

        Для двухсторонних карт используется первая
        сторона, у которой присутствует image_uris.
        """

        image_uris = card_data.get("image_uris")

        image_url = self._get_url_from_image_uris(image_uris)

        if image_url:
            return image_url

        card_faces = card_data.get(
            "card_faces",
            [],
        )

        if not isinstance(card_faces, list):
            return None

        for card_face in card_faces:
            if not isinstance(card_face, dict):
                continue

            face_image_uris = card_face.get("image_uris")

            image_url = self._get_url_from_image_uris(face_image_uris)

            if image_url:
                return image_url

        return None

    def get_cache_path(
        self,
        card_data,
        image_url=None,
    ):
        if image_url is None:
            image_url = self.get_image_url(card_data)

        cache_key = self._build_cache_key(
            card_data=card_data,
            image_url=image_url,
        )

        return self.cache_directory / f"{cache_key}.png"

    def clear_cache(self):
        """
        Удаляет миниатюры из локального кэша.
        """

        removed_files = 0

        for cache_file in self.cache_directory.glob("*.png"):
            try:
                cache_file.unlink()
                removed_files += 1
            except OSError:
                continue

        return removed_files

    # ======================================================
    # Image URL
    # ======================================================

    @staticmethod
    def _get_url_from_image_uris(
        image_uris,
    ):
        if not isinstance(image_uris, dict):
            return None

        for image_size in (
            "small",
            "normal",
            "large",
            "png",
        ):
            image_url = image_uris.get(image_size)

            if image_url:
                return str(image_url).strip()

        return None

    # ======================================================
    # Cache
    # ======================================================

    def _load_from_cache(
        self,
        cache_path,
    ):
        if not cache_path.exists():
            return None

        try:
            with Image.open(cache_path) as cached_image:
                image = cached_image.convert("RGB")

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

    def _save_to_cache(
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

            except OSError as error:
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

                raise ScryfallThumbnailError(
                    "Не удалось сохранить " "изображение в кэш"
                ) from error

    # ======================================================
    # Download
    # ======================================================

    def _download_image(
        self,
        image_url,
    ):
        try:
            response = self.session.get(
                image_url,
                headers=self.headers,
                timeout=self.timeout,
            )

        except requests.RequestException as error:
            raise ScryfallThumbnailError(
                "Ошибка подключения при загрузке " "изображения карты"
            ) from error

        status_code = getattr(
            response,
            "status_code",
            0,
        )

        if not (200 <= status_code < 300):
            raise ScryfallThumbnailError(
                "Scryfall не вернул изображение: " f"HTTP {status_code}"
            )

        image_content = getattr(
            response,
            "content",
            b"",
        )

        if not image_content:
            raise ScryfallThumbnailError("Scryfall вернул пустое изображение")

        try:
            with Image.open(BytesIO(image_content)) as downloaded_image:
                image = downloaded_image.convert("RGB")

                image.load()

                return image

        except (
            OSError,
            ValueError,
        ) as error:
            raise ScryfallThumbnailError(
                "Получены некорректные данные " "изображения"
            ) from error

    # ======================================================
    # Resize
    # ======================================================

    @staticmethod
    def _resize_image(
        image,
        size,
    ):
        if not isinstance(size, tuple) or len(size) != 2:
            raise ValueError("Размер изображения должен быть " "кортежем из двух чисел")

        width = int(size[0])
        height = int(size[1])

        if width <= 0 or height <= 0:
            raise ValueError("Размер изображения должен быть " "больше нуля")

        try:
            resampling = Image.Resampling.LANCZOS
        except AttributeError:
            resampling = Image.LANCZOS

        return ImageOps.contain(
            image=image,
            size=(
                width,
                height,
            ),
            method=resampling,
        )

    # ======================================================
    # Cache key
    # ======================================================

    def _build_cache_key(
        self,
        card_data,
        image_url,
    ):
        card_id = str(
            card_data.get(
                "id",
                "",
            )
        ).strip()

        if card_id:
            return self._sanitize_filename(card_id)

        set_code = str(
            card_data.get(
                "set",
                "",
            )
        ).strip()

        collector_number = str(
            card_data.get(
                "collector_number",
                "",
            )
        ).strip()

        language = str(
            card_data.get(
                "lang",
                "",
            )
        ).strip()

        composed_key = "_".join(
            value
            for value in (
                set_code,
                collector_number,
                language,
            )
            if value
        )

        if composed_key:
            return self._sanitize_filename(composed_key)

        digest_source = str(image_url or card_data).encode(
            "utf-8",
            errors="ignore",
        )

        return hashlib.sha256(digest_source).hexdigest()

    @staticmethod
    def _sanitize_filename(
        value,
    ):
        normalized = re.sub(
            r"[^A-Za-z0-9._-]+",
            "_",
            str(value),
        )

        normalized = normalized.strip("._")

        if not normalized:
            return "unknown_card"

        return normalized
