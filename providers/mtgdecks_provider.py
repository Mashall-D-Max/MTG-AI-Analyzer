import re

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT
from meta.archetype import Archetype
from meta.meta_snapshot import MetaSnapshot
from providers.base_provider import BaseProvider


class MTGDecksProvider(BaseProvider):
    """
    Provider для работы с mtgdecks.net.

    Первая версия:
    - строит URL для форматов;
    - скачивает HTML;
    - парсит meta snapshot из HTML;
    - возвращает данные в наших внутренних моделях.
    """

    BASE_URL = "https://mtgdecks.net"

    FORMAT_ALIASES = {
        "standard": "Standard",
        "pioneer": "Pioneer",
        "explorer": "Explorer",
        "modern": "Modern",
        "legacy": "Legacy",
        "vintage": "Vintage",
        "commander": "Commander",
        "pauper": "Pauper",
    }

    PERCENT_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")

    LINE_META_PATTERN = re.compile(r"^(.+?)[\-\—\|]\s*(\d+(?:[.,]\d+)?)\s*%")

    @property
    def name(self):
        return "MTGDecks"

    def is_available(self):
        try:
            response = requests.get(
                self.BASE_URL,
                headers=self._headers(),
                timeout=REQUEST_TIMEOUT,
            )

            return response.status_code == 200

        except requests.RequestException:
            return False

    def normalize_format_name(self, format_name):
        key = str(format_name).strip().lower()

        if key in self.FORMAT_ALIASES:
            return self.FORMAT_ALIASES[key]

        return str(format_name).strip()

    def build_format_url(self, format_name):
        normalized = self.normalize_format_name(format_name)

        return f"{self.BASE_URL}/{normalized}"

    def build_decklists_url(self, format_name):
        normalized = self.normalize_format_name(format_name)

        return f"{self.BASE_URL}/{normalized}/decklists"

    def build_winrates_url(self, format_name):
        normalized = self.normalize_format_name(format_name)

        return f"{self.BASE_URL}/{normalized}/winrates"

    def get_meta(self, format_name):
        url = self.build_format_url(format_name)

        html = self._get_html(url)

        return self.parse_meta_html(
            html=html,
            format_name=format_name,
        )

    def get_decklists_page(self, format_name):
        url = self.build_decklists_url(format_name)

        return self._get_html(url)

    def get_winrates_page(self, format_name):
        url = self.build_winrates_url(format_name)

        return self._get_html(url)

    def parse_meta_html(self, html, format_name):
        """
        Парсит HTML страницы меты.

        На первом этапе используем best-effort парсер:
        - сначала ищем строки таблиц;
        - потом пробуем искать строки вида:
          Archetype — 14%
        """

        normalized_format = self.normalize_format_name(format_name)

        snapshot = MetaSnapshot(
            format_name=normalized_format,
            source_name=self.name,
        )

        soup = BeautifulSoup(html, "html.parser")

        self._parse_table_rows(
            soup=soup,
            snapshot=snapshot,
            format_name=normalized_format,
        )

        if snapshot.count == 0:
            self._parse_text_lines(
                soup=soup,
                snapshot=snapshot,
                format_name=normalized_format,
            )

        return snapshot

    def _parse_table_rows(self, soup, snapshot, format_name):
        rows = soup.find_all("tr")

        for row in rows:
            cells = [
                cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])
            ]

            if len(cells) < 2:
                continue

            row_text = " ".join(cells)

            meta_share = self._extract_percent(row_text)

            if meta_share is None:
                continue

            name = self._extract_archetype_name_from_cells(cells)

            if not name:
                continue

            snapshot.add_archetype(
                Archetype(
                    name=name,
                    format_name=format_name,
                    meta_share=meta_share,
                )
            )

    def _parse_text_lines(self, soup, snapshot, format_name):
        text = soup.get_text("\n", strip=True)

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            match = self.LINE_META_PATTERN.match(line)

            if not match:
                continue

            name = self._clean_text(match.group(1))

            meta_share = self._to_float(match.group(2))

            if not name:
                continue

            snapshot.add_archetype(
                Archetype(
                    name=name,
                    format_name=format_name,
                    meta_share=meta_share,
                )
            )

    def _extract_archetype_name_from_cells(self, cells):
        for cell in cells:
            clean_cell = self._clean_text(cell)

            if not clean_cell:
                continue

            if self.PERCENT_PATTERN.search(clean_cell):
                continue

            lower_cell = clean_cell.lower()

            if lower_cell in (
                "deck",
                "decks",
                "meta",
                "share",
                "winrate",
                "win rate",
                "price",
                "colors",
                "archetype",
            ):
                continue

            if len(clean_cell) > 80:
                continue

            return clean_cell

        return None

    def _extract_percent(self, text):
        match = self.PERCENT_PATTERN.search(text)

        if not match:
            return None

        return self._to_float(match.group(1))

    def _to_float(self, value):
        value = str(value).replace(",", ".")

        try:
            return float(value)
        except ValueError:
            return 0.0

    def _clean_text(self, text):
        return " ".join(str(text).split()).strip()

    def _get_html(self, url):
        response = requests.get(
            url,
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return response.text

    def _headers(self):
        return {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        }
