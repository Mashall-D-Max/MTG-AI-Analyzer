from gui.scryfall_card_preview import (
    build_card_details,
)

print("=" * 60)
print("SCRYFALL CARD PREVIEW TEST")
print("=" * 60)


card_data = {
    "name": "Aang, Swift Savior",
    "mana_cost": "{1}{W}{U}",
    "type_line": ("Legendary Creature — Human Avatar"),
    "oracle_text": ("Flash\n" "When Aang enters, exile target spell."),
    "power": "2",
    "toughness": "3",
    "set": "tla",
    "set_name": ("Avatar: The Last Airbender"),
    "collector_number": "12",
    "released_at": "2025-11-21",
    "rarity": "rare",
    "lang": "en",
    "artist": "Test Artist",
    "games": [
        "paper",
        "arena",
    ],
    "prices": {
        "usd": "3.50",
        "eur": "2.80",
        "tix": None,
    },
    "legalities": {
        "standard": "legal",
        "pioneer": "legal",
        "modern": "not_legal",
        "commander": "legal",
    },
}


details = build_card_details(card_data)

print(details)


expected_parts = [
    "Aang, Swift Savior",
    "Мана: {1}{W}{U}",
    ("Тип: Legendary Creature — " "Human Avatar"),
    "Oracle-текст:",
    "Сила / выносливость: 2 / 3",
    ("Набор: Avatar: The Last Airbender " "[TLA] № 12"),
    "Редкость: Rare",
    "Художник: Test Artist",
    "USD: 3.50",
    "EUR: 2.80",
    "Standard: легальна",
    "Pioneer: легальна",
    "Commander: легальна",
]


for expected_part in expected_parts:
    if expected_part not in details:
        raise RuntimeError("В описании отсутствует часть: " f"{expected_part}")


if "Modern:" in details:
    raise RuntimeError("Нелегальные форматы не должны " "показываться в кратком списке")


double_faced_card = {
    "name": "Front Side // Back Side",
    "set": "tst",
    "set_name": "Test Set",
    "collector_number": "1",
    "rarity": "mythic",
    "card_faces": [
        {
            "name": "Front Side",
            "mana_cost": "{1}{U}",
            "type_line": "Creature — Wizard",
            "oracle_text": "Draw a card.",
            "power": "2",
            "toughness": "2",
        },
        {
            "name": "Back Side",
            "type_line": "Land",
            "oracle_text": "{T}: Add {U}.",
        },
    ],
}


double_details = build_card_details(double_faced_card)

if "=== Front Side ===" not in double_details:
    raise RuntimeError("Первая сторона карты не отображена")

if "=== Back Side ===" not in double_details:
    raise RuntimeError("Вторая сторона карты не отображена")

if "Draw a card." not in double_details:
    raise RuntimeError("Oracle-текст первой стороны отсутствует")

if "{T}: Add {U}." not in double_details:
    raise RuntimeError("Oracle-текст второй стороны отсутствует")


print()
print("DOUBLE-FACED CARD")
print(double_details)

print()
print("RESULT: OK")
