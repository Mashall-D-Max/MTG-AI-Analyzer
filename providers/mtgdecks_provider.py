import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT
from meta.archetype import Archetype
from meta.meta_snapshot import MetaSnapshot
from parsers.decklist_parser import DecklistParser
from providers.base_provider import BaseProvider


class MTGDecksProvider(BaseProvider):
    """
    Provider для работы с mtgdecks.net.

    Возможности:
    - загрузка страницы меты формата;
    - парсинг MetaSnapshot;
    - загрузка конкретной decklist-страницы;
    - преобразование decklist-страницы в Deck.
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

    CARD_TYPES = (
        "Creature",
        "Instant",
        "Sorcery",
        "Artifact",
        "Enchantment",
        "Planeswalker",
        "Battle",
        "Land",
    )

    PERCENT_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")

    LINE_META_PATTERN = re.compile(r"^(.+?)[\-\—\|]\s*(\d+(?:[.,]\d+)?)\s*%")

    SECTION_PATTERN = re.compile(
        r"^(Creature|Instant|Sorcery|Artifact|Enchantment|Planeswalker|Battle|Land)\s+\[\d+\]$",
        re.IGNORECASE,
    )

    SIDEBOARD_PATTERN = re.compile(
        r"^Sideboard\s+\[\d+\]$",
        re.IGNORECASE,
    )

    CARD_LINE_PATTERN = re.compile(r"^(\d+)\s+(.+)$")

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

    # ======================================================
    # Meta
    # ======================================================

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

    # ======================================================
    # Deck loading
    # ======================================================

    def get_deck(self, url):
        """
        Загрузить конкретную колоду с MTGDecks URL.
        """

        normalized_url = self._normalize_url(url)

        html = self._get_html(normalized_url)

        return self.parse_deck_html(html)

    def parse_deck_html(self, html):
        """
        Преобразовать HTML страницы MTGDecks decklist в Deck.
        """

        deck_text = self.extract_deck_text(html)

        if not deck_text:
            raise RuntimeError("Не удалось найти decklist на странице MTGDecks")

        return DecklistParser().parse_text(deck_text)

    def extract_deck_text(self, html):
        """
        Извлекает decklist из HTML.

        Сначала пытаемся вытащить структурированный список:
        Creature [..], Instant [..], Land [..], Sideboard [..].

        Возвращаем текст в формате:

        Deck
        4 Fatal Push
        ...
        Sideboard
        2 Duress
        """

        soup = BeautifulSoup(html, "html.parser")

        lines = [
            self._clean_text(line)
            for line in soup.get_text("\n", strip=True).splitlines()
        ]

        result = ["Deck"]

        in_deck_section = False
        in_sideboard = False
        found_cards = False

        for line in lines:
            if not line:
                continue

            if self._is_stop_line(line):
                if found_cards:
                    break

            if self.SECTION_PATTERN.match(line):
                in_deck_section = True
                continue

            if self.SIDEBOARD_PATTERN.match(line):
                in_deck_section = True
                in_sideboard = True
                result.append("Sideboard")
                continue

            if not in_deck_section:
                continue

            parsed = self._parse_mtgdecks_card_line(line)

            if parsed is None:
                continue

            quantity, card_name = parsed

            if not card_name:
                continue

            result.append(f"{quantity} {card_name}")

            found_cards = True

        if not found_cards:
            return ""

        return "\n".join(result)

    def _parse_mtgdecks_card_line(self, line):
        match = self.CARD_LINE_PATTERN.match(line)

        if not match:
            return None

        quantity_text = match.group(1)
        rest = match.group(2)

        try:
            quantity = int(quantity_text)
        except ValueError:
            return None

        card_name = self._clean_card_name_from_row(rest)

        if not card_name:
            return None

        return quantity, card_name

    def _clean_card_name_from_row(self, text):
        text = self._clean_text(text)

        if " $" in text:
            text = text.split(" $", 1)[0]

        text = re.sub(
            r"\s+[CURM]\s*$",
            "",
            text,
        )

        text = self._clean_text(text)

        bad_values = {
            "Image",
            "Visual view",
            "List view",
            "Copy to clipboard",
        }

        if text in bad_values:
            return ""

        return text

    def _is_stop_line(self, line):
        lower_line = line.lower()

        stop_markers = (
            "buy this deck",
            "deck tools",
            "export & save",
            "embedding code",
            "hover a card",
            "report deck error",
            "last update",
        )

        return any(marker in lower_line for marker in stop_markers)

    # ======================================================
    # Helpers
    # ======================================================

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

    def _normalize_url(self, url):
        url = str(url).strip()

        if url.startswith("http://") or url.startswith("https://"):
            return url

        return urljoin(
            self.BASE_URL,
            url,
        )

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
