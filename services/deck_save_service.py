import re
from pathlib import Path


class DeckSaveError(RuntimeError):
    pass


class DeckSaveService:
    """
    Экспорт текущей колоды в текстовые форматы.

    Поддерживаются:
    - Arena TXT;
    - обычный TXT;
    - TXT с точными изданиями Scryfall.
    """

    ARENA = "arena"
    PLAIN_TEXT = "plain_txt"
    EXACT_TEXT = "exact_txt"

    EXPORT_FORMAT_LABELS = {
        "Arena TXT": ARENA,
        "Обычный TXT": PLAIN_TEXT,
        "TXT с точными изданиями": EXACT_TEXT,
    }

    DEFAULT_LIBRARY_DIRECTORY = Path("decks") / "saved"

    WINDOWS_RESERVED_NAMES = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{number}" for number in range(1, 10)),
        *(f"LPT{number}" for number in range(1, 10)),
    }

    @classmethod
    def export_format_labels(cls):
        return list(cls.EXPORT_FORMAT_LABELS.keys())

    @classmethod
    def resolve_export_format(cls, value):
        normalized = str(value or "").strip()

        if normalized in cls.EXPORT_FORMAT_LABELS:
            return cls.EXPORT_FORMAT_LABELS[normalized]

        if normalized in cls.EXPORT_FORMAT_LABELS.values():
            return normalized

        raise ValueError(
            f"Неизвестный формат сохранения: {value}"
        )

    @classmethod
    def sanitize_deck_name(cls, deck_name):
        name = str(deck_name or "").strip()

        if not name:
            name = "Новая колода"

        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", name)
        name = re.sub(r"\s+", " ", name)
        name = name.rstrip(". ")

        if not name:
            name = "Новая колода"

        if name.upper() in cls.WINDOWS_RESERVED_NAMES:
            name = f"_{name}"

        return name[:120]

    @classmethod
    def sanitize_folder_name(cls, value):
        return cls.sanitize_deck_name(value).replace(" ", "_")

    @classmethod
    def build_filename(cls, deck_name, export_format):
        cls.resolve_export_format(export_format)
        safe_name = cls.sanitize_deck_name(deck_name)
        return f"{safe_name}.txt"

    @classmethod
    def build_internal_path(
        cls,
        deck_name,
        game_format,
        export_format,
        root_directory=None,
    ):
        root = Path(
            root_directory
            if root_directory is not None
            else cls.DEFAULT_LIBRARY_DIRECTORY
        )

        format_folder = cls.sanitize_folder_name(
            game_format or "Без формата"
        )

        export_label = next(
            (
                label
                for label, code in cls.EXPORT_FORMAT_LABELS.items()
                if code == cls.resolve_export_format(export_format)
            ),
            str(export_format),
        )
        export_folder = cls.sanitize_folder_name(export_label)

        return (
            root
            / format_folder
            / export_folder
            / cls.build_filename(deck_name, export_format)
        )

    @classmethod
    def build_deck_text(
        cls,
        deck,
        deck_name,
        game_format,
        export_format,
    ):
        if deck is None:
            raise ValueError("Колода не указана")

        resolved_format = cls.resolve_export_format(
            export_format
        )

        if resolved_format == cls.ARENA:
            return cls._build_arena_text(deck)

        if resolved_format == cls.PLAIN_TEXT:
            return cls._build_plain_text(
                deck=deck,
                deck_name=deck_name,
                game_format=game_format,
            )

        return cls._build_exact_text(
            deck=deck,
            deck_name=deck_name,
            game_format=game_format,
        )

    @classmethod
    def save_to_path(
        cls,
        deck,
        deck_name,
        game_format,
        export_format,
        path,
    ):
        output_path = Path(path)

        if output_path.suffix.lower() != ".txt":
            output_path = output_path.with_suffix(".txt")

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        text = cls.build_deck_text(
            deck=deck,
            deck_name=deck_name,
            game_format=game_format,
            export_format=export_format,
        )

        try:
            output_path.write_text(
                text,
                encoding="utf-8",
            )
        except OSError as error:
            raise DeckSaveError(
                f"Не удалось сохранить колоду: {error}"
            ) from error

        return output_path

    @classmethod
    def save_internal(
        cls,
        deck,
        deck_name,
        game_format,
        export_format,
        root_directory=None,
    ):
        path = cls.build_internal_path(
            deck_name=deck_name,
            game_format=game_format,
            export_format=export_format,
            root_directory=root_directory,
        )

        return cls.save_to_path(
            deck=deck,
            deck_name=deck_name,
            game_format=game_format,
            export_format=export_format,
            path=path,
        )

    @classmethod
    def _build_arena_text(cls, deck):
        lines = ["Deck"]

        for deck_card in getattr(deck, "cards", []):
            lines.append(
                cls._format_arena_line(deck_card)
            )

        sideboard = list(
            getattr(deck, "sideboard", [])
        )

        if sideboard:
            lines.extend(["", "Sideboard"])

            for deck_card in sideboard:
                lines.append(
                    cls._format_arena_line(deck_card)
                )

        return "\n".join(lines).rstrip() + "\n"

    @classmethod
    def _build_plain_text(
        cls,
        deck,
        deck_name,
        game_format,
    ):
        lines = [
            f"# Название: {cls.sanitize_deck_name(deck_name)}",
            f"# Формат: {game_format}",
            "",
            "Deck",
        ]

        for deck_card in getattr(deck, "cards", []):
            lines.append(
                cls._format_plain_line(deck_card)
            )

        sideboard = list(
            getattr(deck, "sideboard", [])
        )

        if sideboard:
            lines.extend(["", "Sideboard"])

            for deck_card in sideboard:
                lines.append(
                    cls._format_plain_line(deck_card)
                )

        return "\n".join(lines).rstrip() + "\n"

    @classmethod
    def _build_exact_text(
        cls,
        deck,
        deck_name,
        game_format,
    ):
        lines = [
            f"# Название: {cls.sanitize_deck_name(deck_name)}",
            f"# Формат: {game_format}",
            "# Издания: точные данные Scryfall, если они доступны",
            "",
            "Deck",
        ]

        for deck_card in getattr(deck, "cards", []):
            lines.append(
                cls._format_exact_line(deck_card)
            )

        sideboard = list(
            getattr(deck, "sideboard", [])
        )

        if sideboard:
            lines.extend(["", "Sideboard"])

            for deck_card in sideboard:
                lines.append(
                    cls._format_exact_line(deck_card)
                )

        return "\n".join(lines).rstrip() + "\n"

    @classmethod
    def _format_plain_line(cls, deck_card):
        quantity = int(
            getattr(deck_card, "quantity", 0)
            or 0
        )

        card_name = cls._card_name(deck_card)

        return f"{quantity} {card_name}"

    @classmethod
    def _format_arena_line(cls, deck_card):
        base_line = cls._format_plain_line(deck_card)
        set_code = cls._printing_value(
            deck_card,
            "set_code",
            "set",
        ).upper()
        collector_number = cls._printing_value(
            deck_card,
            "collector_number",
            "collector_number",
        )

        if set_code and collector_number:
            return (
                f"{base_line} ({set_code}) "
                f"{collector_number}"
            )

        if set_code:
            return f"{base_line} ({set_code})"

        return base_line

    @classmethod
    def _format_exact_line(cls, deck_card):
        base_line = cls._format_plain_line(deck_card)
        printing_label = str(
            getattr(deck_card, "printing_label", "")
            or ""
        ).strip()

        if printing_label:
            return f"{base_line} {printing_label}"

        return base_line

    @staticmethod
    def _card_name(deck_card):
        name = str(
            getattr(deck_card, "name", "")
            or ""
        ).strip()

        if name:
            return name

        card = getattr(deck_card, "card", None)
        name = str(
            getattr(card, "name", "Без названия")
            or "Без названия"
        ).strip()

        return name or "Без названия"

    @staticmethod
    def _printing_value(
        deck_card,
        property_name,
        dictionary_key,
    ):
        value = str(
            getattr(deck_card, property_name, "")
            or ""
        ).strip()

        if value:
            return value

        printing_data = getattr(
            deck_card,
            "printing_data",
            None,
        )

        if isinstance(printing_data, dict):
            return str(
                printing_data.get(dictionary_key, "")
                or ""
            ).strip()

        return ""
