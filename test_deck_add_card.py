from models.deck import Deck


class FakeCard:
    def __init__(self, name):
        self.name = name


print("=" * 60)
print("DECK ADD CARD TEST")
print("=" * 60)


deck = Deck()
card = FakeCard("Aang, Swift Savior")

printing_data = {
    "id": "printing-1",
    "name": "Aang, Swift Savior",
    "set": "tla",
    "collector_number": "12",
    "lang": "en",
}

first_row = deck.add_card(
    card=card,
    quantity=2,
    printing_data=printing_data,
)

second_row = deck.add_card(
    card=FakeCard("Aang, Swift Savior"),
    quantity=1,
)

if first_row is not second_row:
    raise RuntimeError(
        "Повторное добавление не объединило карту"
    )

if deck.mainboard_size != 3:
    raise RuntimeError(
        "Неверный размер mainboard: "
        f"{deck.mainboard_size}"
    )

if deck.unique_cards != 1:
    raise RuntimeError(
        "В mainboard появилась лишняя строка"
    )

if first_row.printing_label != "[TLA · № 12 · en]":
    raise RuntimeError(
        "Неверная подпись издания: "
        f"{first_row.printing_label}"
    )

sideboard_row = deck.add_sideboard_card(
    card=FakeCard("Aang, Swift Savior"),
    quantity=2,
    printing_data=printing_data,
)

if deck.sideboard_size != 2:
    raise RuntimeError(
        "Неверный размер sideboard"
    )

if sideboard_row is first_row:
    raise RuntimeError(
        "Mainboard и sideboard должны хранить "
        "отдельные строки"
    )

removed = deck.remove_card(
    "Aang, Swift Savior",
    quantity=2,
)

if not removed:
    raise RuntimeError(
        "Удаление карты не выполнено"
    )

if deck.mainboard_size != 1:
    raise RuntimeError(
        "Количество после удаления неверно"
    )

print("Mainboard:", deck.mainboard_size)
print("Sideboard:", deck.sideboard_size)
print("Printing:", first_row.printing_label)
print()
print("RESULT: OK")
