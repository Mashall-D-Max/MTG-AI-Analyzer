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

    PERCENT_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")

    LINE_META_PATTERN = re.compile(r"^(.+?)[\-\—\|]\s*(\d+(?:[.,]\d+)?)\s*%")

    SECTION_PATTERN = re.compile(
        r"^(Creature|Instant|Sorcery|Artifact|Enchantment|Planeswalker|Battle|Land)\s*[\[\(]\d+[\]\)]$",
        re.IGNORECASE,
    )

    MAINDECK_PATTERN = re.compile(
        r"^Maindeck\s*[\[\(]\d+[\]\)]$",
        re.IGNORECASE,
    )

    SIDEBOARD_PATTERN = re.compile(
        r"^Sideboard(?:\s*[\[\(]\d+[\]\)])?$",
        re.IGNORECASE,
    )

    CARD_LINE_PATTERN = re.compile(r"^(\d{1,2})\s+(.+)$")

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

        Приоритет:
        1. Export block после Copy to clipboard and import!
        2. Структурированные секции Creature/Instant/Land/Sideboard
        """

        export_text = self._extract_export_deck_text(html)

        if export_text:
            return export_text

        structured_text = self._extract_structured_deck_text(html)

        if structured_text:
            return structured_text

        return ""

    def _extract_export_deck_text(self, html):
        lines = self._html_to_lines(html)

        marker_index = self._find_export_marker_index(lines)

        if marker_index is None:
            return ""

        deck_index = self._find_deck_marker_index(
            lines=lines,
            start_index=marker_index,
        )

        if deck_index is None:
            return ""

        return self._parse_lines_to_deck_text(
            lines=lines,
            start_index=deck_index + 1,
            require_sections=False,
        )

    def _extract_structured_deck_text(self, html):
        lines = self._html_to_lines(html)

        return self._parse_lines_to_deck_text(
            lines=lines,
            start_index=0,
            require_sections=True,
        )

    def _parse_lines_to_deck_text(
        self,
        lines,
        start_index=0,
        require_sections=False,
    ):
        result = ["Deck"]

        in_deck_area = not require_sections
        in_card_section = not require_sections
        in_sideboard = False
        sideboard_added = False
        found_cards = False
        invalid_after_cards = 0

        index = start_index

        while index < len(lines):
            line = lines[index]

            if not line:
                index += 1
                continue

            if self._is_stop_line(line):
                if found_cards:
                    break

                index += 1
                continue

            if self.MAINDECK_PATTERN.match(line):
                in_deck_area = True
                in_card_section = False
                in_sideboard = False
                index += 1
                continue

            if self.SECTION_PATTERN.match(line):
                in_deck_area = True
                in_card_section = True
                index += 1
                continue

            if self.SIDEBOARD_PATTERN.match(line):
                in_deck_area = True
                in_card_section = True
                in_sideboard = True

                if not sideboard_added:
                    result.append("Sideboard")
                    sideboard_added = True

                index += 1
                continue

            if require_sections and (not in_deck_area or not in_card_section):
                index += 1
                continue

            parsed = self._parse_card_from_lines(
                lines=lines,
                index=index,
            )

            if parsed is None:
                if found_cards:
                    invalid_after_cards += 1

                    if invalid_after_cards >= 25:
                        break

                index += 1
                continue

            quantity, card_name, next_index = parsed

            if in_sideboard and not sideboard_added:
                result.append("Sideboard")
                sideboard_added = True

            result.append(f"{quantity} {card_name}")

            found_cards = True
            invalid_after_cards = 0
            index = next_index

        if not found_cards:
            return ""

        return "\n".join(result)

    def _parse_card_from_lines(self, lines, index):
        line = lines[index]

        same_line = self._parse_mtgdecks_card_line(line)

        if same_line is not None:
            quantity, card_name = same_line

            return quantity, card_name, index + 1

        if not self._is_quantity_line(line):
            return None

        quantity = int(line)

        next_index = index + 1

        max_index = min(
            len(lines),
            index + 7,
        )

        while next_index < max_index:
            candidate = lines[next_index]

            if self._is_quantity_line(candidate):
                return None

            if self.SECTION_PATTERN.match(candidate):
                return None

            if self.SIDEBOARD_PATTERN.match(candidate):
                return None

            if self._is_stop_line(candidate):
                return None

            if self._is_probable_card_name(candidate):
                card_name = self._clean_card_name_from_row(candidate)

                if self._is_probable_card_name(card_name):
                    return quantity, card_name, next_index + 1

            next_index += 1

        return None

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

        if not self._is_probable_card_name(card_name):
            return None

        return quantity, card_name

    def _clean_card_name_from_row(self, text):
        text = self._clean_text(text)

        garbage_markers = (
            "$",
            "€",
            " tix",
            "@cardhoarder",
            "@tcgplayer",
            "@cardkingdom",
            "hover a card",
            "report deck error",
            "last update",
            "add/remove",
            "collection quantity",
            "visual view",
            "list view",
            "copy to clipboard",
        )

        lower_text = text.lower()

        for marker in garbage_markers:
            index = lower_text.find(marker)

            if index != -1:
                text = text[:index]
                lower_text = text.lower()

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
            "Quantity",
            "Collection",
            "Deck",
            "Sideboard",
        }

        if text in bad_values:
            return ""

        return text

    def _is_quantity_line(self, line):
        return (
            re.fullmatch(
                r"\d{1,2}",
                line,
            )
            is not None
        )

    def _is_probable_card_name(self, line):
        if not line:
            return False

        line = self._clean_text(line)

        if not line:
            return False

        if len(line) > 90:
            return False

        if self._is_quantity_line(line):
            return False

        if line.isdigit():
            return False

        if not any(char.isalpha() for char in line):
            return False

        if self.SECTION_PATTERN.match(line):
            return False

        if self.SIDEBOARD_PATTERN.match(line):
            return False

        if self._is_stop_line(line):
            return False

        lower_line = line.lower()

        bad_markers = (
            "$",
            "€",
            " tix",
            "@cardhoarder",
            "@tcgplayer",
            "@cardkingdom",
            "hover a card",
            "report deck error",
            "last update",
            "add/remove",
            "collection quantity",
            "visual view",
            "deck view",
            "arena export",
            "tools & download",
            "copy to clipboard",
            "magic online format",
            "apprentice and mws",
        )

        for marker in bad_markers:
            if marker in lower_line:
                return False

        bad_values = {
            "image",
            "visual view",
            "deck view",
            "arena export",
            "tools & download",
            "copy to clipboard",
            "magic online format",
            "apprentice and mws .dec",
            "quantity",
            "collection",
            "deck",
            "sideboard",
        }

        if lower_line in bad_values:
            return False

        if re.fullmatch(r"[CURM]", line):
            return False

        return True

    def _is_stop_line(self, line):
        lower_line = line.lower()

        stop_markers = (
            "buy this deck",
            "deck tools",
            "export & save",
            "embedding code",
            "hover a card",
            "hover a card name",
            "report deck error",
            "last update",
            "if you find any error",
            "layout footer",
            "never miss important",
            "add/remove card to collection",
            "collection quantity",
            "magic online format",
            "apprentice and mws",
            "arena export",
            "visual view",
            "list view",
            "tools & download",
        )

        return any(marker in lower_line for marker in stop_markers)

    def _html_to_lines(self, html):
        soup = BeautifulSoup(html, "html.parser")

        return [
            self._clean_text(line)
            for line in soup.get_text("\n", strip=True).splitlines()
            if self._clean_text(line)
        ]

    def _find_export_marker_index(self, lines):
        for index, line in enumerate(lines):
            lower_line = line.lower()

            if "copy to clipboard and import" in lower_line:
                return index

        return None

    def _find_deck_marker_index(self, lines, start_index):
        for index in range(start_index, len(lines)):
            line = lines[index].strip().lower()

            if line == "deck":
                return index

            if self._is_stop_line(lines[index]):
                return None

        return None

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

        if not url:
            raise ValueError("Пустая ссылка MTGDecks")

        lower_url = url.lower()

        marker = "mtgdecks.net"

        if marker in lower_url:
            marker_index = lower_url.find(marker)

            clean_part = url[marker_index:]

            clean_part = clean_part.lstrip("/")

            return f"https://{clean_part}"

        if url.startswith("/"):
            return urljoin(
                self.BASE_URL,
                url,
            )

        raise ValueError(
            "Некорректная ссылка MTGDecks. " "Ссылка должна содержать mtgdecks.net"
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
