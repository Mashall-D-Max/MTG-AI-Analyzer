from meta.meta_compare import MetaCompare
from models.deck import Deck


class FakeCard:
    def __init__(self, name):
        self.name = name


def make_deck(cards):
    deck = Deck()

    for card_name, quantity in cards:
        deck.add_card(
            FakeCard(card_name),
            quantity,
        )

    return deck


user_deck = make_deck(
    [
        ("Fatal Push", 4),
        ("Thoughtseize", 4),
        ("Plains", 2),
    ]
)

meta_deck = make_deck(
    [
        ("Fatal Push", 4),
        ("Thoughtseize", 2),
        ("Duress", 2),
        ("Plains", 2),
    ]
)

comparison = MetaCompare().compare_decks(
    user_deck,
    meta_deck,
)

print("=" * 60)
print("META COMPARE BASIC TEST")
print("=" * 60)

print("Similarity:", comparison["similarity"])
print("Missing:", comparison["missing_cards"])
print("Extra:", comparison["extra_cards"])
print("Matched:", comparison["matched_cards"])

if comparison["similarity"] != 80.0:
    raise RuntimeError(
        f"Ожидалось similarity 80.0, получено {comparison['similarity']}"
    )

if comparison["missing_cards"].get("Duress") != 2:
    raise RuntimeError("Ожидалось, что не хватает 2 Duress")

if comparison["extra_cards"].get("Thoughtseize") != 2:
    raise RuntimeError("Ожидалось, что лишние 2 Thoughtseize")

print()
print("RESULT: OK")
