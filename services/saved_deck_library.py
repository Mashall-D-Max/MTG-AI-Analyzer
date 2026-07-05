import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from models.deck import Deck
from services.deck_save_service import DeckSaveService


@dataclass(frozen=True)
class SavedDeckEntry:
    path: Path
    deck_name: str
    game_format: str
    export_format: str
    export_format_label: str
    modified_at: datetime
    size_bytes: int

    @property
    def modified_text(self):
        return self.modified_at.strftime("%d.%m.%Y %H:%M")

    @property
    def size_text(self):
        if self.size_bytes < 1024:
            return f"{self.size_bytes} Б"

        return f"{self.size_bytes / 1024:.1f} КБ"


@dataclass(frozen=True)
class ParsedDeckRow:
    zone: str
    quantity: int
    card_name: str
    printing_data: dict | None


class SavedDeckLibraryService:
    """
    Работа с внутренней библиотекой сохранённых колод.

    Библиотека расположена в decks/saved и содержит файлы,
    созданные DeckSaveService.
    """

    EXACT_LINE_PATTERN = re.compile(
        r"^(?P<quantity>\d+)\s+"
        r"(?P<name>.+?)\s+"
        r"\[\s*(?P<set>[^·\]]+?)\s*"
        r"·\s*№\s*(?P<number>[^·\]]+?)"
        r"(?:\s*·\s*(?P<lang>[^\]]+?))?\s*\]\s*$"
    )

    ARENA_LINE_PATTERN = re.compile(
        r"^(?P<quantity>\d+)\s+"
        r"(?P<name>.+?)"
        r"(?:\s+\((?P<set>[A-Za-z0-9]+)\)"
        r"(?:\s+(?P<number>\S+))?)?\s*$"
    )

    HEADER_NAME_PATTERN = re.compile(
        r"^#\s*Название\s*:\s*(?P<value>.+?)\s*$",
        re.IGNORECASE,
    )

    HEADER_FORMAT_PATTERN = re.compile(
        r"^#\s*Формат\s*:\s*(?P<value>.+?)\s*$",
        re.IGNORECASE,
    )

    @classmethod
    def scan(cls, root_directory=None):
        root = Path(
            root_directory
            if root_directory is not None
            else DeckSaveService.DEFAULT_LIBRARY_DIRECTORY
        )

        if not root.exists():
            return []

        entries = []

        for path in root.rglob("*.txt"):
            if not path.is_file():
                continue

            try:
                text = path.read_text(
                    encoding="utf-8-sig",
                    errors="replace",
                )
                stat = path.stat()
            except OSError:
                continue

            game_format, export_format_label = (
                cls._infer_path_metadata(
                    path=path,
                    root=root,
                )
            )

            header_name = cls._extract_header(
                text,
                cls.HEADER_NAME_PATTERN,
            )
            header_format = cls._extract_header(
                text,
                cls.HEADER_FORMAT_PATTERN,
            )

            deck_name = header_name or path.stem
            game_format = header_format or game_format

            export_format = cls._resolve_export_format(
                export_format_label=export_format_label,
                text=text,
            )

            export_format_label = (
                cls._label_for_export_format(
                    export_format
                )
            )

            entries.append(
                SavedDeckEntry(
                    path=path,
                    deck_name=deck_name,
                    game_format=game_format,
                    export_format=export_format,
                    export_format_label=(
                        export_format_label
                    ),
                    modified_at=datetime.fromtimestamp(
                        stat.st_mtime
                    ),
                    size_bytes=stat.st_size,
                )
            )

        entries.sort(
            key=lambda item: item.modified_at,
            reverse=True,
        )

        return entries

    @classmethod
    def parse_deck_text(cls, text):
        rows = []
        current_zone = Deck.MAINBOARD

        for raw_line in str(text or "").splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            lowered = line.casefold()

            if lowered in {"deck", "mainboard"}:
                current_zone = Deck.MAINBOARD
                continue

            if lowered in {"sideboard", "side"}:
                current_zone = Deck.SIDEBOARD
                continue

            if lowered.startswith("sb:"):
                current_zone = Deck.SIDEBOARD
                line = line[3:].strip()

            exact_match = cls.EXACT_LINE_PATTERN.match(
                line
            )

            if exact_match:
                printing_data = {
                    "set": exact_match.group("set")
                    .strip()
                    .lower(),
                    "collector_number": exact_match.group(
                        "number"
                    ).strip(),
                }

                language = exact_match.group("lang")

                if language:
                    printing_data["lang"] = (
                        language.strip()
                    )

                rows.append(
                    ParsedDeckRow(
                        zone=current_zone,
                        quantity=int(
                            exact_match.group("quantity")
                        ),
                        card_name=exact_match.group(
                            "name"
                        ).strip(),
                        printing_data=printing_data,
                    )
                )
                continue

            arena_match = cls.ARENA_LINE_PATTERN.match(
                line
            )

            if not arena_match:
                raise ValueError(
                    "Не удалось распознать строку "
                    f"сохранённой колоды: {line}"
                )

            printing_data = None
            set_code = arena_match.group("set")
            collector_number = arena_match.group(
                "number"
            )

            if set_code or collector_number:
                printing_data = {}

                if set_code:
                    printing_data["set"] = (
                        set_code.strip().lower()
                    )

                if collector_number:
                    printing_data["collector_number"] = (
                        collector_number.strip()
                    )

            rows.append(
                ParsedDeckRow(
                    zone=current_zone,
                    quantity=int(
                        arena_match.group("quantity")
                    ),
                    card_name=arena_match.group(
                        "name"
                    ).strip(),
                    printing_data=printing_data,
                )
            )

        return rows

    @classmethod
    def load_deck(
        cls,
        entry,
        card_loader=None,
    ):
        if not isinstance(entry, SavedDeckEntry):
            raise TypeError(
                "Ожидалась запись сохранённой колоды"
            )

        try:
            text = entry.path.read_text(
                encoding="utf-8-sig",
            )
        except OSError as error:
            raise RuntimeError(
                f"Не удалось прочитать колоду: {error}"
            ) from error

        rows = cls.parse_deck_text(text)

        if not rows:
            raise ValueError(
                "Сохранённая колода не содержит карт"
            )

        if card_loader is None:
            from api.scryfall import get_card

            card_loader = get_card

        deck = Deck()

        for row in rows:
            card = card_loader(row.card_name)

            if card is None:
                raise ValueError(
                    f"Карта не найдена: {row.card_name}"
                )

            if row.zone == Deck.SIDEBOARD:
                deck.add_sideboard_card(
                    card=card,
                    quantity=row.quantity,
                    printing_data=row.printing_data,
                )
            else:
                deck.add_card(
                    card=card,
                    quantity=row.quantity,
                    printing_data=row.printing_data,
                )

        return deck

    @staticmethod
    def delete(entry):
        if not isinstance(entry, SavedDeckEntry):
            raise TypeError(
                "Ожидалась запись сохранённой колоды"
            )

        try:
            entry.path.unlink()
        except OSError as error:
            raise RuntimeError(
                f"Не удалось удалить колоду: {error}"
            ) from error


    @classmethod
    def _infer_path_metadata(
        cls,
        path,
        root,
    ):
        try:
            relative = path.relative_to(root)
            parts = relative.parts
        except ValueError:
            parts = path.parts

        game_format = "Без формата"
        export_format_label = "Обычный TXT"

        if len(parts) >= 3:
            game_format = parts[-3].replace("_", " ")
            export_folder = parts[-2]

            for label in (
                DeckSaveService.export_format_labels()
            ):
                if (
                    DeckSaveService.sanitize_folder_name(
                        label
                    )
                    == export_folder
                ):
                    export_format_label = label
                    break

        return game_format, export_format_label

    @classmethod
    def _resolve_export_format(
        cls,
        export_format_label,
        text,
    ):
        try:
            return DeckSaveService.resolve_export_format(
                export_format_label
            )
        except ValueError:
            pass

        if "# Издания: точные данные Scryfall" in text:
            return DeckSaveService.EXACT_TEXT

        for line in text.splitlines():
            if cls.EXACT_LINE_PATTERN.match(
                line.strip()
            ):
                return DeckSaveService.EXACT_TEXT

        for line in text.splitlines():
            stripped = line.strip()

            if (
                stripped
                and not stripped.startswith("#")
                and cls.ARENA_LINE_PATTERN.match(stripped)
                and re.search(
                    r"\([A-Za-z0-9]+\)(?:\s+\S+)?$",
                    stripped,
                )
            ):
                return DeckSaveService.ARENA

        return DeckSaveService.PLAIN_TEXT

    @staticmethod
    def _label_for_export_format(export_format):
        for label, code in (
            DeckSaveService.EXPORT_FORMAT_LABELS.items()
        ):
            if code == export_format:
                return label

        return "Обычный TXT"

    @staticmethod
    def _extract_header(text, pattern):
        for line in str(text or "").splitlines():
            match = pattern.match(line.strip())

            if match:
                return match.group("value").strip()

        return ""
