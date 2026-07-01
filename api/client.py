import time
from io import BytesIO
from urllib.parse import urlsplit, urlunsplit

import requests
from PIL import Image

from config import (
    IMAGE_TIMEOUT,
    REQUEST_TIMEOUT,
    SCRYFALL_429_DELAY,
    SCRYFALL_API,
    SCRYFALL_REQUEST_DELAY,
    USER_AGENT,
)
from utils.logger import logger


class ScryfallClient:
    """
    Клиент для работы со Scryfall API и загрузки изображений.
    """

    RETRY_COUNT = 3
    RETRY_DELAY = 1

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            }
        )

        self._last_request_at = 0

    def get_card(self, name):
        url = f"{SCRYFALL_API}/cards/named"

        for attempt in range(self.RETRY_COUNT):
            try:
                self._wait_for_rate_limit()

                response = self.session.get(
                    url,
                    params={"exact": name},
                    timeout=REQUEST_TIMEOUT,
                )

                if response.status_code == 429:
                    delay = self._get_retry_after(response)

                    logger.warning(
                        f"Scryfall rate limit. Ждём {delay} сек. " f"Карта: {name}"
                    )

                    time.sleep(delay)
                    continue

                if response.status_code == 404:
                    response.raise_for_status()

                response.raise_for_status()

                return response.json()

            except requests.RequestException as error:
                logger.warning(
                    f"[{attempt + 1}/{self.RETRY_COUNT}] "
                    f"Ошибка загрузки карты {name}: {error}"
                )

                if attempt < self.RETRY_COUNT - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise

        raise RuntimeError(f"Не удалось загрузить карту после повторов: {name}")

    def get_image(self, url):
        """
        Загрузить изображение карты.
        """

        urls_to_try = [
            url,
            self._remove_query_params(url),
        ]

        last_error = None

        for image_url in urls_to_try:
            if not image_url:
                continue

            try:
                return self._download_image(image_url)

            except requests.RequestException as error:
                last_error = error

                logger.warning(f"Ошибка загрузки изображения: {image_url} | {error}")

        if last_error:
            raise last_error

        raise RuntimeError("Не удалось загрузить изображение карты")

    def _download_image(self, url):
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*",
        }

        for attempt in range(self.RETRY_COUNT):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=IMAGE_TIMEOUT,
                )

                response.raise_for_status()

                image = Image.open(BytesIO(response.content))

                return image.convert("RGB")

            except requests.RequestException as error:
                logger.warning(
                    f"[{attempt + 1}/{self.RETRY_COUNT}] "
                    f"Ошибка загрузки изображения: {error}"
                )

                if attempt < self.RETRY_COUNT - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise

    def _wait_for_rate_limit(self):
        now = time.monotonic()

        elapsed = now - self._last_request_at

        if elapsed < SCRYFALL_REQUEST_DELAY:
            time.sleep(SCRYFALL_REQUEST_DELAY - elapsed)

        self._last_request_at = time.monotonic()

    def _get_retry_after(self, response):
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                return max(
                    float(retry_after),
                    SCRYFALL_429_DELAY,
                )
            except ValueError:
                pass

        return SCRYFALL_429_DELAY

    def _remove_query_params(self, url):
        if not url:
            return None

        parts = urlsplit(url)

        return urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                "",
                "",
            )
        )


client = ScryfallClient()
