from services.deck_export_service import DeckExportService

DECK_TEXT = """Deck
4 Fatal Push
4 Thoughtseize

Sideboard
2 Duress
"""


print("=" * 60)
print("DECK EXPORT SERVICE TEST")
print("=" * 60)

path = DeckExportService().save_deck_text(
    deck_text=DECK_TEXT,
    filename="test_upgraded_deck.txt",
    folder="decks",
)

print("Saved:", path)

if not path.exists():
    raise RuntimeError("Файл не был создан")

saved_text = path.read_text(
    encoding="utf-8",
)

if "4 Fatal Push" not in saved_text:
    raise RuntimeError("В сохранённом файле нет Fatal Push")

if "2 Duress" not in saved_text:
    raise RuntimeError("В сохранённом файле нет Duress")

print()
print("RESULT: OK")
