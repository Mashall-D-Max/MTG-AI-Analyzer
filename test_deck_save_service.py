from pathlib import Path
from tempfile import TemporaryDirectory

from models.deck import Deck
from services.deck_save_service import DeckSaveService


class DummyCard:
    def __init__(self, name):
        self.name = name


print("=" * 60)
print("DECK SAVE SERVICE TEST")
print("=" * 60)


deck = Deck()
deck.add_card(
    card=DummyCard("Aang, Swift Savior"),
    quantity=4,
    printing_data={
        "id": "aang-test-printing",
        "set": "tla",
        "collector_number": "12",
        "lang": "en",
    },
)
deck.add_card(
    card=DummyCard("Plains"),
    quantity=20,
)
deck.add_sideboard_card(
    card=DummyCard("Negate"),
    quantity=2,
    printing_data={
        "set": "m21",
        "collector_number": "59",
        "lang": "en",
    },
)

arena_text = DeckSaveService.build_deck_text(
    deck=deck,
    deck_name="Azorius Flash",
    game_format="Pioneer",
    export_format="Arena TXT",
)

expected_arena_parts = [
    "Deck",
    "4 Aang, Swift Savior (TLA) 12",
    "20 Plains",
    "Sideboard",
    "2 Negate (M21) 59",
]

for part in expected_arena_parts:
    if part not in arena_text:
        raise RuntimeError(
            f"Arena export is missing: {part}"
        )

plain_text = DeckSaveService.build_deck_text(
    deck=deck,
    deck_name="Azorius Flash",
    game_format="Pioneer",
    export_format="Обычный TXT",
)

if "# Название: Azorius Flash" not in plain_text:
    raise RuntimeError("Deck name is missing in TXT export")

if "# Формат: Pioneer" not in plain_text:
    raise RuntimeError("Game format is missing in TXT export")

if "[TLA" in plain_text:
    raise RuntimeError(
        "Plain TXT export must not contain printing labels"
    )

exact_text = DeckSaveService.build_deck_text(
    deck=deck,
    deck_name="Azorius Flash",
    game_format="Pioneer",
    export_format="TXT с точными изданиями",
)

if "4 Aang, Swift Savior [TLA · № 12 · en]" not in exact_text:
    raise RuntimeError(
        "Exact TXT export did not preserve printing data"
    )

if "2 Negate [M21 · № 59 · en]" not in exact_text:
    raise RuntimeError(
        "Sideboard printing data was not preserved"
    )

with TemporaryDirectory() as temporary_directory:
    saved_path = DeckSaveService.save_internal(
        deck=deck,
        deck_name='Azorius: Flash / Test',
        game_format="Pioneer",
        export_format="Arena TXT",
        root_directory=temporary_directory,
    )

    if not saved_path.exists():
        raise RuntimeError("Saved deck file does not exist")

    if saved_path.parent.parent.name != "Pioneer":
        raise RuntimeError(
            "Unexpected game format folder: "
            f"{saved_path.parent.parent.name}"
        )

    if saved_path.parent.name != "Arena_TXT":
        raise RuntimeError(
            "Unexpected export format folder: "
            f"{saved_path.parent.name}"
        )

    if any(symbol in saved_path.name for symbol in '<>:"/\\|?*'):
        raise RuntimeError(
            f"Filename contains invalid symbols: {saved_path.name}"
        )

    saved_text = Path(saved_path).read_text(
        encoding="utf-8"
    )

    if saved_text != arena_text:
        raise RuntimeError(
            "Saved file differs from generated Arena export"
        )

    print("Saved:", saved_path)

print("Arena export: OK")
print("Plain TXT export: OK")
print("Exact printing TXT export: OK")
print()
print("RESULT: OK")
