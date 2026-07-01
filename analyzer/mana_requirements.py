import re
from collections import Counter


class ManaRequirementsAnalyzer:

    COLORS = ["W", "U", "B", "R", "G"]

    def __init__(self, deck):
        self.deck = deck

    def analyze(self):

        requirements = Counter()

        for deck_card in self.deck.cards:

            mana_cost = deck_card.card.mana_cost or ""

            for color in self.COLORS:

                count = len(re.findall(r"\{" + color + r"\}", mana_cost))

                if count > 0:
                    requirements[color] += count * deck_card.quantity

        return requirements
