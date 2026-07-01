from pathlib import Path

from importers.deck_format import DeckFormat


class FormatDetector:
    """
    Определение формата источника колоды.
    """

    @staticmethod
    def detect(source) -> DeckFormat:

        source_text = str(source).strip()

        lower_source = source_text.lower()

        if lower_source.startswith("http://") or lower_source.startswith("https://"):

            if "moxfield.com" in lower_source:
                return DeckFormat.MOXFIELD

            if "archidekt.com" in lower_source:
                return DeckFormat.ARCHIDEKT

            if "mtgdecks.net" in lower_source:
                return DeckFormat.MTGDECKS

            return DeckFormat.URL

        if "\n" in source_text:

            lines = FormatDetector._get_non_empty_lines(source_text)

            if FormatDetector._looks_like_arena(lines):
                return DeckFormat.ARENA

            return DeckFormat.CLIPBOARD

        path = Path(source_text)

        if path.exists() and path.is_file():

            try:

                file_text = path.read_text(encoding="utf-8")

                lines = FormatDetector._get_non_empty_lines(file_text)

                if FormatDetector._looks_like_arena(lines):
                    return DeckFormat.ARENA

            except OSError:
                pass

        if path.suffix.lower() == ".txt":
            return DeckFormat.TXT

        return DeckFormat.CLIPBOARD

    @staticmethod
    def _get_non_empty_lines(text):

        return [
            line.strip().lstrip("\ufeff") for line in text.splitlines() if line.strip()
        ]

    @staticmethod
    def _looks_like_arena(lines):

        if not lines:
            return False

        first_line = lines[0].lower()

        return first_line in ("deck", "sideboard")
