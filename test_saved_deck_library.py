from tempfile import TemporaryDirectory

from models.deck import Deck
from services.deck_save_service import DeckSaveService
from services.saved_deck_library import (
    SavedDeckLibraryService,
)


class DummyCard:
    def __init__(self, name):
        self.name = name


print("=" * 60)
print("SAVED DECK LIBRARY TEST")
print("=" * 60)


deck = Deck()
deck.add_card(
    card=DummyCard("Aang, Swift Savior"),
    quantity=4,
    printing_data={
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


with TemporaryDirectory() as temporary_directory:
    saved_paths = []

    for export_format in (
        "Arena TXT",
        "Обычный TXT",
        "TXT с точными изданиями",
    ):
        saved_paths.append(
            DeckSaveService.save_internal(
                deck=deck,
                deck_name="Azorius Flash",
                game_format="Pioneer",
                export_format=export_format,
                root_directory=temporary_directory,
            )
        )

    entries = SavedDeckLibraryService.scan(
        temporary_directory
    )

    if len(entries) != 3:
        raise RuntimeError(
            "В библиотеке ожидалось 3 файла, "
            f"получено: {len(entries)}"
        )

    labels = {
        entry.export_format_label
        for entry in entries
    }

    expected_labels = {
        "Arena TXT",
        "Обычный TXT",
        "TXT с точными изданиями",
    }

    if labels != expected_labels:
        raise RuntimeError(
            f"Неверные форматы библиотеки: {labels}"
        )

    exact_entry = next(
        entry
        for entry in entries
        if entry.export_format_label
        == "TXT с точными изданиями"
    )

    loaded_deck = SavedDeckLibraryService.load_deck(
        exact_entry,
        card_loader=DummyCard,
    )

    if loaded_deck.mainboard_size != 24:
        raise RuntimeError(
            "Неверный размер Mainboard после загрузки"
        )

    if loaded_deck.sideboard_size != 2:
        raise RuntimeError(
            "Неверный размер Sideboard после загрузки"
        )

    first_card = loaded_deck.cards[0]

    if first_card.set_code != "TLA":
        raise RuntimeError(
            "Код точного издания не восстановлен"
        )

    if first_card.collector_number != "12":
        raise RuntimeError(
            "Номер коллекционера не восстановлен"
        )

    if first_card.language != "en":
        raise RuntimeError(
            "Язык точного издания не восстановлен"
        )

    SavedDeckLibraryService.delete(exact_entry)

    entries_after_delete = (
        SavedDeckLibraryService.scan(
            temporary_directory
        )
    )

    if len(entries_after_delete) != 2:
        raise RuntimeError(
            "Удаление колоды не отразилось в библиотеке"
        )

    print("Found:", len(entries))
    print("Formats:", ", ".join(sorted(labels)))
    print("Loaded Mainboard:", loaded_deck.mainboard_size)
    print("Loaded Sideboard:", loaded_deck.sideboard_size)
    print("Printing:", first_card.printing_label)
    print("After delete:", len(entries_after_delete))

print()
print("RESULT: OK")
