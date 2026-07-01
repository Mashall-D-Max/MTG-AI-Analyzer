from collections import Counter


class ColorAnalyzer:
    """
    Анализ цветовой принадлежности карт в колоде.
    """

    def __init__(self, deck):
        self.deck = deck

    def calculate(self):

        colors = Counter()

        for deck_card in self.deck.cards:

            card = deck_card.card

            for color in card.colors or []:
                colors[color] += deck_card.quantity

        return dict(sorted(colors.items()))
