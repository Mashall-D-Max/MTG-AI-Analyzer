from importers.deck_format import DeckFormat


class FormatDetector:
    """
    Определение формата колоды.
    """

    @staticmethod
    def detect(source: str) -> DeckFormat:

        source = source.strip()

        if source.startswith("http"):

            if "moxfield.com" in source:
                return DeckFormat.MOXFIELD

            if "archidekt.com" in source:
                return DeckFormat.ARCHIDEKT

            if "mtgdecks.net" in source:
                return DeckFormat.MTGDECKS

            return DeckFormat.URL

        if source.endswith(".txt"):
            return DeckFormat.TXT

        return DeckFormat.CLIPBOARD
