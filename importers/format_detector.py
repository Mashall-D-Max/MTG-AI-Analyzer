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

        path = Path(source_text)

        if path.suffix.lower() == ".txt":
            return DeckFormat.TXT

        lines = [line.strip() for line in source_text.splitlines() if line.strip()]

        if lines:

            first_line = lines[0].lower()

            if first_line in ("deck", "sideboard"):
                return DeckFormat.ARENA

        return DeckFormat.CLIPBOARD
