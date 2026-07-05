from models.deck import Deck


class FakeCard:
    def __init__(self, name):
        self.name = name


print("=" * 60)
print("DECK EDITING TEST")
print("=" * 60)


deck = Deck()

fatal_push = FakeCard("Fatal Push")
duress = FakeCard("Duress")

printing_mkm = {
    "id": "fatal-push-mkm",
    "name": "Fatal Push",
    "set": "mkm",
    "collector_number": "84",
    "lang": "en",
}

printing_2xm = {
    "id": "fatal-push-2xm",
    "name": "Fatal Push",
    "set": "2xm",
    "collector_number": "93",
    "lang": "en",
}

main_row = deck.add_card(
    card=fatal_push,
    quantity=4,
    printing_data=printing_mkm,
)

side_row = deck.add_sideboard_card(
    card=duress,
    quantity=2,
)

if deck.mainboard_size != 4:
    raise RuntimeError("Неверный исходный mainboard")

if deck.sideboard_size != 2:
    raise RuntimeError("Неверный исходный sideboard")

updated = deck.set_quantity(
    zone="mainboard",
    index=0,
    quantity=3,
)

if updated is not main_row:
    raise RuntimeError(
        "Изменение количества заменило объект строки"
    )

if deck.mainboard_size != 3:
    raise RuntimeError(
        "set_quantity не изменил размер mainboard"
    )

increased = deck.change_quantity(
    zone="main",
    index=0,
    delta=2,
)

if increased.quantity != 5:
    raise RuntimeError(
        "Увеличение количества сработало неверно"
    )

moved = deck.move_card(
    source_zone="mainboard",
    index=0,
    target_zone="sideboard",
)

if deck.mainboard_size != 0:
    raise RuntimeError(
        "Карта осталась в mainboard после переноса"
    )

if deck.sideboard_size != 7:
    raise RuntimeError(
        "Неверный размер sideboard после переноса"
    )

if moved.printing_label != "[MKM · № 84 · en]":
    raise RuntimeError(
        "При переносе потеряно точное издание"
    )

merged = deck.add_sideboard_card(
    card=FakeCard("Fatal Push"),
    quantity=1,
    printing_data=printing_mkm,
)

if merged is not moved:
    raise RuntimeError(
        "Одинаковое издание не объединилось"
    )

if merged.quantity != 6:
    raise RuntimeError(
        "Количество после объединения неверно"
    )

different_printing = deck.add_sideboard_card(
    card=FakeCard("Fatal Push"),
    quantity=2,
    printing_data=printing_2xm,
)

if different_printing is moved:
    raise RuntimeError(
        "Разные издания ошибочно объединились"
    )

if deck.unique_sideboard_cards != 3:
    raise RuntimeError(
        "Неверное количество строк sideboard"
    )

removed = deck.remove_at(
    zone="sideboard",
    index=0,
)

if removed is not side_row:
    raise RuntimeError(
        "Удалена не та строка sideboard"
    )

if deck.sideboard_size != 8:
    raise RuntimeError(
        "Неверный размер sideboard после удаления"
    )

removed_by_zero = deck.set_quantity(
    zone="sideboard",
    index=1,
    quantity=0,
)

if removed_by_zero is not None:
    raise RuntimeError(
        "Количество 0 должно удалить строку"
    )

if deck.sideboard_size != 6:
    raise RuntimeError(
        "Удаление через количество 0 не сработало"
    )

print("Mainboard:", deck.mainboard_size)
print("Sideboard:", deck.sideboard_size)
print("Rows:", deck.unique_sideboard_cards)
print("Printing:", moved.printing_label)
print()
print("RESULT: OK")
