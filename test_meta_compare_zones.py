from meta.meta_compare import MetaCompare
from models.deck import Deck


class FakeCard:
    def __init__(self, name):
        self.name = name


def make_deck(mainboard, sideboard):
    deck = Deck()

    for card_name, quantity in mainboard:
        deck.add_card(
            FakeCard(card_name),
            quantity,
        )

    for card_name, quantity in sideboard:
        deck.add_sideboard_card(
            FakeCard(card_name),
            quantity,
        )

    return deck


user_deck = make_deck(
    mainboard=[
        ("Fatal Push", 4),
        ("Thoughtseize", 4),
        ("Plains", 2),
    ],
    sideboard=[
        ("Duress", 2),
        ("Go Blank", 2),
    ],
)

meta_deck = make_deck(
    mainboard=[
        ("Fatal Push", 4),
        ("Thoughtseize", 2),
        ("Duress", 2),
        ("Plains", 2),
    ],
    sideboard=[
        ("Duress", 2),
        ("Rest in Peace", 2),
    ],
)

comparison = MetaCompare().compare_all_zones(
    user_deck,
    meta_deck,
)

print("=" * 60)
print("META COMPARE ZONES TEST")
print("=" * 60)

print("Overall:", comparison["overall"]["similarity"])
print("Mainboard:", comparison["mainboard"]["similarity"])
print("Sideboard:", comparison["sideboard"]["similarity"])

print()
print("Main missing:", comparison["mainboard"]["missing_cards"])
print("Main extra:", comparison["mainboard"]["extra_cards"])

print()
print("Side missing:", comparison["sideboard"]["missing_cards"])
print("Side extra:", comparison["sideboard"]["extra_cards"])

if comparison["mainboard"]["similarity"] != 80.0:
    raise RuntimeError("Ожидалось 80.0% совпадения mainboard")

if comparison["sideboard"]["similarity"] != 50.0:
    raise RuntimeError("Ожидалось 50.0% совпадения sideboard")

if comparison["overall"]["similarity"] != 71.43:
    raise RuntimeError(
        f"Ожидалось 71.43% overall, получено {comparison['overall']['similarity']}"
    )

print()
print("RESULT: OK")
