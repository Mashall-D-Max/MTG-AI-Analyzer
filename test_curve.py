from parsers.deck_parser import load_deck

from analyzer.mana_curve import ManaCurve
from analyzer.colors import ColorAnalyzer
from analyzer.card_types import CardTypeAnalyzer
from analyzer.mana_base import ManaBaseAnalyzer

deck = load_deck("decks/test.txt")

print("=" * 60)
print("DECK SUMMARY")
print("=" * 60)

print(f"Cards        : {deck.size}")
print(f"Unique cards : {deck.unique_cards}")

print()

print("=" * 60)
print("MANA CURVE")
print("=" * 60)

curve = ManaCurve(deck).calculate()

for cmc in sorted(curve):
    print(f"CMC {cmc}: {curve[cmc]}")

print()

print("=" * 60)
print("COLORS")
print("=" * 60)

colors = ColorAnalyzer(deck).calculate()

names = {
    "W": "White",
    "U": "Blue",
    "B": "Black",
    "R": "Red",
    "G": "Green",
}

for color in names:
    print(f"{names[color]:6}: {colors.get(color,0)}")

print()

print("=" * 60)
print("CARD TYPES")
print("=" * 60)

types = CardTypeAnalyzer(deck).calculate()

for t in [
    "Creature",
    "Instant",
    "Sorcery",
    "Artifact",
    "Enchantment",
    "Planeswalker",
    "Land",
]:
    print(f"{t:13}: {types.get(t,0)}")

print()

print("=" * 60)
print("MANA SOURCES")
print("=" * 60)

sources = ManaBaseAnalyzer(deck).analyze()

for color in names:
    print(f"{names[color]:6}: {sources.get(color,0)}")
