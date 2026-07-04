import threading
import time
from urllib.parse import urlparse

import requests


class ScryfallSearchError(RuntimeError):
    """
    Ошибка обращения к поисковому API Scryfall.
    """


class ScryfallSearchClient:
    """
    Клиент расширенного поиска Scryfall.

    Возвращает исходные JSON-данные.
    Преобразование в модели приложения добавим
    на этапе подключения нового интерфейса.
    """

    BASE_URL = "https://api.scryfall.com"

    def __init__(
        self,
        session=None,
        timeout=20,
        min_request_interval=0.55,
        max_retries=3,
    ):
        self.session = session or requests.Session()
        self.timeout = timeout
        self.min_request_interval = min_request_interval
        self.max_retries = max_retries

        self.headers = {
            "Accept": "application/json",
            "User-Agent": (
                "MTG-AI-Analyzer/0.1 " "(desktop deck analysis application)"
            ),
        }

        self._request_lock = threading.Lock()
        self._last_request_time = 0.0

    # ======================================================
    # Card search
    # ======================================================

    def search_cards(
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
            raise ValueError("Поисковый запрос Scryfall пустой")

        params = {
            "q": query,
            "page": max(
                1,
                int(page),
            ),
            "unique": unique,
            "order": order,
            "dir": direction,
            "include_extras": ("true" if include_extras else "false"),
        }

        return self._request(
            "/cards/search",
            params=params,
        )

    def search_next_page(self, next_page_url):
        if not next_page_url:
            raise ValueError("Ссылка следующей страницы отсутствует")

        return self._request(next_page_url)

    # ======================================================
    # Autocomplete
    # ======================================================

    def autocomplete(
        self,
        query,
        include_extras=False,
    ):
        query = str(query).strip()

        if not query:
            return []

        result = self._request(
            "/cards/autocomplete",
            params={
                "q": query,
                "include_extras": ("true" if include_extras else "false"),
            },
        )

        return result.get(
            "data",
            [],
        )

    # ======================================================
    # Sets
    # ======================================================

    def get_all_sets(self):
        result = self._request("/sets")

        return result.get(
            "data",
            [],
        )

    # ======================================================
    # Random card
    # ======================================================

    def get_random_card(self, query=None):
        params = None

        if query:
            params = {
                "q": str(query).strip(),
            }

        return self._request(
            "/cards/random",
            params=params,
        )

    # ======================================================
    # HTTP
    # ======================================================

    def _request(
        self,
        path_or_url,
        params=None,
    ):
        url = self._build_url(path_or_url)

        last_error = None

        for attempt in range(
            1,
            self.max_retries + 1,
        ):
            self._wait_for_rate_limit()

            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout,
                )

            except requests.RequestException as error:
                last_error = error

                if attempt >= self.max_retries:
                    break

                time.sleep(self._retry_delay(attempt))
                continue

            if response.status_code == 429:
                last_error = ScryfallSearchError(
                    "Scryfall временно ограничил " "частоту запросов"
                )

                if attempt >= self.max_retries:
                    break

                time.sleep(
                    self._retry_after(
                        response,
                        attempt,
                    )
                )
                continue

            if 500 <= response.status_code < 600:
                last_error = ScryfallSearchError(
                    "Временная ошибка сервера Scryfall: " f"HTTP {response.status_code}"
                )

                if attempt >= self.max_retries:
                    break

                time.sleep(self._retry_delay(attempt))
                continue

            return self._parse_response(response)

        raise ScryfallSearchError(
            "Не удалось выполнить запрос к Scryfall"
        ) from last_error

    def _parse_response(self, response):
        try:
            payload = response.json()
        except ValueError as error:
            raise ScryfallSearchError("Scryfall вернул некорректный JSON") from error

        if 200 <= response.status_code < 300:
            return payload

        details = payload.get(
            "details",
            "Неизвестная ошибка Scryfall",
        )

        raise ScryfallSearchError(f"{details} " f"(HTTP {response.status_code})")

    def _wait_for_rate_limit(self):
        with self._request_lock:
            now = time.monotonic()

            elapsed = now - self._last_request_time

            remaining = self.min_request_interval - elapsed

            if remaining > 0:
                time.sleep(remaining)

            self._last_request_time = time.monotonic()

    def _retry_after(
        self,
        response,
        attempt,
    ):
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                return max(
                    float(retry_after),
                    self.min_request_interval,
                )
            except ValueError:
                pass

        return self._retry_delay(attempt)

    @staticmethod
    def _retry_delay(attempt):
        return min(
            0.75 * attempt,
            3.0,
        )

    def _build_url(self, path_or_url):
        path_or_url = str(path_or_url).strip()

        if path_or_url.startswith("https://"):
            parsed = urlparse(path_or_url)

            if parsed.netloc != "api.scryfall.com":
                raise ValueError("Разрешены только ссылки API Scryfall")

            return path_or_url

        if not path_or_url.startswith("/"):
            path_or_url = "/" + path_or_url

        return self.BASE_URL + path_or_url
