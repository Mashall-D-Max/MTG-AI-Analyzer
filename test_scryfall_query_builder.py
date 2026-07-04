from services.scryfall_query_builder import (
    ScryfallQueryBuilder,
)

print("=" * 60)
print("SCRYFALL QUERY BUILDER TEST")
print("=" * 60)


filters = {
    "raw_query": "-is:funny",
    "name": "Aang",
    "oracle": "flash",
    "types": [
        "creature",
        "legendary",
    ],
    "colors": [
        "W",
        "U",
    ],
    "color_comparison": ">=",
    "identity": [
        "W",
        "U",
    ],
    "identity_comparison": "<=",
    "mana_cost": "{1}{W}{U}",
    "mana_value": 3,
    "mana_value_operator": "<=",
    "power": 2,
    "power_operator": ">=",
    "games": [
        "paper",
        "arena",
    ],
    "format_status": "legal",
    "format": "pioneer",
    "sets": [
        "tla",
        "mkm",
    ],
    "rarities": [
        "r",
        "m",
    ],
    "criteria": [
        "legendary",
        "booster",
    ],
    "price_currency": "usd",
    "price_operator": "<=",
    "price_value": 10,
    "artist": "John Doe",
    "language": "en",
}


query = ScryfallQueryBuilder.build(filters)

print(query)


expected_parts = [
    "-is:funny",
    'name:"Aang"',
    'oracle:"flash"',
    "(type:creature OR type:legendary)",
    "color>=WU",
    "id<=WU",
    'mana:"{1}{W}{U}"',
    "mv<=3",
    "power>=2",
    "(game:paper OR game:arena)",
    "legal:pioneer",
    "(set:tla OR set:mkm)",
    "(rarity:r OR rarity:m)",
    "is:legendary",
    "is:booster",
    "usd<=10",
    'artist:"John Doe"',
    "lang:en",
]


for expected_part in expected_parts:
    if expected_part not in query:
        raise RuntimeError("В запросе отсутствует часть: " f"{expected_part}")


colorless_query = ScryfallQueryBuilder.build(
    {
        "colors": ["C"],
        "color_comparison": "=",
    }
)

if colorless_query != "color=C":
    raise RuntimeError("Некорректный запрос бесцветной карты: " f"{colorless_query}")


empty_query = ScryfallQueryBuilder.build({})

if empty_query != "":
    raise RuntimeError("Пустые фильтры должны создавать " "пустую строку")


print()
print("RESULT: OK")
