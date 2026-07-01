from models.deck_card import DeckCard


class Deck:

    def __init__(self):

        self.cards = []

    def add_card(self, card, quantity=1):

        self.cards.append(DeckCard(card, quantity))

    @property
    def size(self):

        return sum(c.quantity for c in self.cards)

    @property
    def unique_cards(self):

        return len(self.cards)
