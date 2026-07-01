from collections import Counter


class CardTypeAnalyzer:
    """
    Анализ типов карт в колоде.
    """

    TYPES = (
        "Creature",
        "Instant",
        "Sorcery",
        "Artifact",
        "Enchantment",
        "Planeswalker",
        "Land",
    )

    def __init__(self, deck):
        self.deck = deck

    def calculate(self):

        result = Counter()

        for deck_card in self.deck.cards:

            card = deck_card.card

            type_line = card.type_line or ""

            for card_type in self.TYPES:

                if card_type in type_line:
                    result[card_type] += deck_card.quantity

        return dict(sorted(result.items()))
