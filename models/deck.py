from models.deck_card import DeckCard


class Deck:
    """
    Модель колоды.

    cards      — mainboard
    sideboard  — sideboard
    """

    def __init__(self):

        self.cards = []
        self.sideboard = []

    def add_card(self, card, quantity=1):

        self.cards.append(DeckCard(card, quantity))

    def add_sideboard_card(self, card, quantity=1):

        self.sideboard.append(DeckCard(card, quantity))

    @property
    def size(self):

        return sum(c.quantity for c in self.cards)

    @property
    def mainboard_size(self):

        return self.size

    @property
    def sideboard_size(self):

        return sum(c.quantity for c in self.sideboard)

    @property
    def total_size(self):

        return self.mainboard_size + self.sideboard_size

    @property
    def unique_cards(self):

        return len(self.cards)

    @property
    def unique_sideboard_cards(self):

        return len(self.sideboard)

    @property
    def all_cards(self):

        return self.cards + self.sideboard
