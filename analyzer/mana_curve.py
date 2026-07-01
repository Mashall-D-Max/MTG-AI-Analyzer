from collections import Counter


class ManaCurve:
    """
    Анализ кривой маны колоды.
    """

    def __init__(self, deck):
        self.deck = deck

    def calculate(self):
        curve = Counter()

        for deck_card in self.deck.cards:
            card = deck_card.card

            cmc = int(card.cmc or 0)

            curve[cmc] += deck_card.quantity

        return dict(sorted(curve.items()))
