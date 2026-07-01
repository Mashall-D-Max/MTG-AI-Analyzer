from meta.deck_upgrade_builder import DeckUpgradeBuilder
from meta.meta_compare import MetaCompare
from models.deck import Deck


class FakeCard:
    def __init__(self, name, mana_cost=""):
        self.name = name
        self.mana_cost = mana_cost


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

reference_deck = make_deck(
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
    reference_deck,
)

deck_text = DeckUpgradeBuilder().build_upgraded_deck_text(
    user_deck=user_deck,
    reference_deck=reference_deck,
    comparison=comparison,
)

print("=" * 60)
print("DECK UPGRADE BUILDER TEST")
print("=" * 60)

print(deck_text)

if "2 Duress" not in deck_text:
    raise RuntimeError("Ожидалось, что Duress будет добавлен")

if "2 Go Blank" in deck_text:
    raise RuntimeError("Go Blank должен быть убран из sideboard")

if "2 Rest in Peace" not in deck_text:
    raise RuntimeError("Rest in Peace должен быть добавлен в sideboard")

lines = deck_text.splitlines()

fatal_push_index = lines.index("4 Fatal Push")
thoughtseize_index = lines.index("2 Thoughtseize")
plains_index = lines.index("2 Plains")
duress_main_index = lines.index("2 Duress")

if not fatal_push_index < thoughtseize_index < plains_index < duress_main_index:
    raise RuntimeError("Порядок mainboard нарушен")

sideboard_index = lines.index("Sideboard")
duress_side_index = lines.index("2 Duress", sideboard_index)
rest_index = lines.index("2 Rest in Peace")

if not sideboard_index < duress_side_index < rest_index:
    raise RuntimeError("Порядок sideboard нарушен")

print()
print("RESULT: OK")
