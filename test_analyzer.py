from analyzer.deck_analyzer import DeckAnalyzer
from parsers.deck_parser import load_deck

deck = load_deck("decks/test.txt")

analysis = DeckAnalyzer(deck).analyze()

print("=" * 60)
print("DECK ANALYSIS")
print("=" * 60)

print()
print("SUMMARY")
print(f"Cards        : {analysis['size']}")
print(f"Unique cards : {analysis['unique_cards']}")

print()
print("MANA CURVE")
for cmc, count in analysis["mana_curve"].items():
    print(f"CMC {cmc}: {count}")

print()
print("COLORS")
for color, count in analysis["colors"].items():
    print(f"{color}: {count}")

print()
print("CARD TYPES")
for card_type, count in analysis["card_types"].items():
    print(f"{card_type}: {count}")

print()
print("MANA SOURCES")
for color, count in analysis["mana_sources"].items():
    print(f"{color}: {count}")

print()
print("MANA REQUIREMENTS")
for color, count in analysis["mana_requirements"].items():
    print(f"{color}: {count}")

print()
print("AI MANA ANALYSIS")
for item in analysis["ai"]:
    status = "OK" if item["ok"] else "NOT ENOUGH"

    print()
    print(item["name"])
    print(f"Requirements : {item['required']}")
    print(f"Sources      : {item['sources']}")
    print(f"Status       : {status}")
    print(f"Difference   : {item['difference']}")
