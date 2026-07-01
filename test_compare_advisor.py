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

if len(recommendations) != 3:
    raise RuntimeError(f"Ожидалось 3 рекомендации, получено {len(recommendations)}")

total_remove = sum(recommendation["quantity"] for recommendation in recommendations)

total_add = sum(recommendation["quantity"] for recommendation in recommendations)

if total_remove != 3:
    raise RuntimeError(f"Ожидалось убрать 3 карты, получено {total_remove}")

if total_add != 3:
    raise RuntimeError(f"Ожидалось добавить 3 карты, получено {total_add}")

print()
print("RESULT: OK")
