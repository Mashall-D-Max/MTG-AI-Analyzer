from models.deck import Deck
from services.deck_format_validator import (
    DeckFormatValidator,
)


class DummyCard:
    def __init__(self, name):
        self.name = name


print("=" * 60)
print("DECK FORMAT VALIDATOR TEST")
print("=" * 60)


pioneer_deck = Deck()
pioneer_deck.add_card(
    DummyCard("Plains"),
    quantity=59,
)

result = DeckFormatValidator.validate(
    pioneer_deck,
    "Pioneer",
)

if result.is_valid:
    raise RuntimeError(
        "Pioneer deck with 59 cards must be invalid"
    )

if "не хватает 1" not in result.to_text():
    raise RuntimeError(
        "Missing-card diagnostic was not generated"
    )

pioneer_deck.add_card(
    DummyCard("Island"),
    quantity=1,
)
pioneer_deck.add_sideboard_card(
    DummyCard("Negate"),
    quantity=15,
)

result = DeckFormatValidator.validate(
    pioneer_deck,
    "Pioneer",
)

if not result.is_valid:
    raise RuntimeError(
        f"60/15 Pioneer deck must be valid: {result.to_text()}"
    )

pioneer_deck.add_sideboard_card(
    DummyCard("Disdainful Stroke"),
    quantity=1,
)

result = DeckFormatValidator.validate(
    pioneer_deck,
    "Pioneer",
)

if result.is_valid:
    raise RuntimeError(
        "Pioneer sideboard with 16 cards must be invalid"
    )

commander_deck = Deck()
commander_deck.add_card(
    DummyCard("Commander Deck Cards"),
    quantity=100,
)

result = DeckFormatValidator.validate(
    commander_deck,
    "Commander",
)

if not result.is_valid:
    raise RuntimeError(
        "Commander deck with 100 mainboard cards must be valid"
    )

commander_deck.add_sideboard_card(
    DummyCard("Sideboard Card"),
    quantity=1,
)

result = DeckFormatValidator.validate(
    commander_deck,
    "Commander",
)

if result.is_valid:
    raise RuntimeError(
        "Commander sideboard must be empty"
    )

brawl_deck = Deck()
brawl_deck.add_card(
    DummyCard("Brawl Cards"),
    quantity=60,
)

if not DeckFormatValidator.validate(
    brawl_deck,
    "Brawl",
).is_valid:
    raise RuntimeError(
        "Brawl deck with 60 cards must be valid"
    )

limited_deck = Deck()
limited_deck.add_card(
    DummyCard("Limited Cards"),
    quantity=40,
)
limited_deck.add_sideboard_card(
    DummyCard("Card Pool"),
    quantity=30,
)

if not DeckFormatValidator.validate(
    limited_deck,
    "Sealed",
).is_valid:
    raise RuntimeError(
        "Sealed deck with 40 mainboard cards must be valid"
    )

print("Pioneer 60/15: OK")
print("Commander 100/0: OK")
print("Brawl 60/0: OK")
print("Sealed 40+: OK")
print()
print("RESULT: OK")
