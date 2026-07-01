from meta.mana_impact_advisor import ManaImpactAdvisor
from models.deck import Deck


class FakeCard:
    def __init__(self, name, mana_cost, type_line="", oracle_text=""):
        self.name = name
        self.mana_cost = mana_cost
        self.type_line = type_line
        self.oracle_text = oracle_text
        self.cmc = 0
        self.colors = []


def add_main(deck, name, quantity, mana_cost):
    deck.add_card(
        FakeCard(
            name=name,
            mana_cost=mana_cost,
        ),
        quantity,
    )


def add_land(deck, name, quantity, oracle_text):
    deck.add_card(
        FakeCard(
            name=name,
            mana_cost="",
            type_line="Land",
            oracle_text=oracle_text,
        ),
        quantity,
    )


user_deck = Deck()

add_main(user_deck, "Thoughtseize", 4, "{B}")
add_main(user_deck, "Go Blank", 2, "{2}{B}")

add_land(user_deck, "Swamp", 8, "{T}: Add {B}.")
add_land(user_deck, "Plains", 2, "{T}: Add {W}.")


class FakeDeckCard:
    def __init__(self, name, mana_cost):
        self.card = FakeCard(
            name=name,
            mana_cost=mana_cost,
        )


comparison = {
    "missing_cards": {
        "Rest in Peace": 2,
    },
    "extra_cards": {
        "Go Blank": 2,
    },
}


user_cards = [
    FakeDeckCard("Go Blank", "{2}{B}"),
]

reference_cards = [
    FakeDeckCard("Rest in Peace", "{1}{W}"),
]


report = ManaImpactAdvisor().analyze(
    user_deck=user_deck,
    comparison=comparison,
    user_deck_cards=user_cards,
    reference_deck_cards=reference_cards,
)

print("=" * 60)
print("MANA IMPACT ADVISOR TEST")
print("=" * 60)

for item in report:
    print(
        item["color"],
        item["sources"],
        item["required"],
        item["difference"],
        item["ok"],
    )

white = next(item for item in report if item["color"] == "W")

black = next(item for item in report if item["color"] == "B")

if white["required"] != 2:
    raise RuntimeError(f"Ожидалось W requirement 2, получено {white['required']}")

if black["required"] != 4:
    raise RuntimeError(f"Ожидалось B requirement 4, получено {black['required']}")

print()
print("RESULT: OK")
