from parsers.deck_parser import load_deck
from analyzer.deck import DeckAnalyzer

print("=" * 60)
print("СТАРТ")
print("=" * 60)

deck = load_deck("decks/test.txt")

print()
print("Размер объекта Deck:", deck.size)

analyzer = DeckAnalyzer(deck)

print()
print("=" * 60)
print("АНАЛИЗ")
print("=" * 60)

analyzer.summary()

print()
print("=" * 60)
print("ГОТОВО")
print("=" * 60)
