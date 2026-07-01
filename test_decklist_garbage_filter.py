from parsers.decklist_parser import DecklistParser

TEXT = """
Deck
4 Fatal Push
4 Thoughtseize
1 Mai, Scornful Striker $41.10 Tix @cardhoarder Hover a card name to see its price
1
3
5
7
9
Sideboard
2 Duress
"""


parser = DecklistParser()

deck = parser.parse_text(TEXT)

print("=" * 60)
print("DECKLIST GARBAGE FILTER TEST")
print("=" * 60)

print("Mainboard:", deck.mainboard_size)
print("Sideboard:", deck.sideboard_size)
print("Total:", deck.total_size)

for deck_card in deck.cards:
    print(deck_card.quantity, deck_card.card.name)

for deck_card in deck.sideboard:
    print("SB", deck_card.quantity, deck_card.card.name)

if deck.mainboard_size != 9:
    raise RuntimeError(f"Ожидалось 9 карт mainboard, получено {deck.mainboard_size}")

if deck.sideboard_size != 2:
    raise RuntimeError(f"Ожидалось 2 карты sideboard, получено {deck.sideboard_size}")

if deck.total_size != 11:
    raise RuntimeError(f"Ожидалось 11 карт всего, получено {deck.total_size}")

card_names = [deck_card.card.name for deck_card in deck.cards]

bad_names = {
    "1",
    "3",
    "5",
    "7",
    "9",
}

for bad_name in bad_names:
    if bad_name in card_names:
        raise RuntimeError(f"Мусорная строка попала как карта: {bad_name}")

print()
print("RESULT: OK")
