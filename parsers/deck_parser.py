from api.scryfall import get_card
from models.deck import Deck


def load_deck(filename):
    """
    Загрузить колоду из текстового файла.
    """

    deck = Deck()

    with open(filename, "r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            parts = line.split(" ", 1)

            if len(parts) != 2:
                continue

            quantity = int(parts[0])
            card_name = parts[1]

            card = get_card(card_name)

            if card is None:
                continue

            deck.add_card(card, quantity)

    return deck
