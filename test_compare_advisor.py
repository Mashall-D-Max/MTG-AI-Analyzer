from meta.compare_advisor import CompareAdvisor


class FakeCard:
    def __init__(self, name, mana_cost):
        self.name = name
        self.mana_cost = mana_cost


class FakeDeckCard:
    def __init__(self, name, mana_cost):
        self.card = FakeCard(
            name,
            mana_cost,
        )


comparison = {
    "missing_cards": {
        "Duress": 2,
        "Rest in Peace": 1,
    },
    "extra_cards": {
        "Thoughtseize": 2,
        "Go Blank": 1,
    },
}


user_cards = [
    FakeDeckCard("Thoughtseize", "{B}"),
    FakeDeckCard("Go Blank", "{2}{B}"),
]

reference_cards = [
    FakeDeckCard("Duress", "{B}"),
    FakeDeckCard("Rest in Peace", "{1}{W}"),
]


recommendations = CompareAdvisor().build_recommendations(
    comparison=comparison,
    user_deck_cards=user_cards,
    reference_deck_cards=reference_cards,
)

print("=" * 60)
print("COMPARE ADVISOR TEST")
print("=" * 60)

for recommendation in recommendations:
    print(
        f"Убрать {recommendation['quantity']} "
        f"{recommendation['remove']} -> "
        f"добавить {recommendation['quantity']} "
        f"{recommendation['add']} | "
        f"{recommendation['mana_change']}"
    )

if len(recommendations) != 3:
    raise RuntimeError(f"Ожидалось 3 рекомендации, получено {len(recommendations)}")

has_mana_change = any(
    recommendation["mana_change"] != "мана: без изменений"
    for recommendation in recommendations
)

if not has_mana_change:
    raise RuntimeError("Ожидалось хотя бы одно изменение по цветам маны")

print()
print("RESULT: OK")
