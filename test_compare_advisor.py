from meta.compare_advisor import CompareAdvisor

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


recommendations = CompareAdvisor().build_recommendations(comparison)

print("=" * 60)
print("COMPARE ADVISOR TEST")
print("=" * 60)

for recommendation in recommendations:
    print(
        f"Убрать {recommendation['quantity']} "
        f"{recommendation['remove']} -> "
        f"добавить {recommendation['quantity']} "
        f"{recommendation['add']}"
    )

if len(recommendations) != 2:
    raise RuntimeError(f"Ожидалось 2 рекомендации, получено {len(recommendations)}")

print()
print("RESULT: OK")
