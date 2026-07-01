import re
from collections import Counter


class ManaBaseAnalyzer:
    """
    Анализ источников маны в колоде.
    """

    COLORS = ("W", "U", "B", "R", "G")

    def __init__(self, deck):
        self.deck = deck

    def analyze(self):

        sources = Counter()

        for deck_card in self.deck.cards:

            card = deck_card.card

            type_line = card.type_line or ""

            if "Land" not in type_line:
                continue

            oracle_text = card.oracle_text or ""

            for color in self.COLORS:

                if re.search(rf"\{{{color}\}}", oracle_text):
                    sources[color] += deck_card.quantity

        return dict(sorted(sources.items()))
