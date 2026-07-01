from api.scryfall import get_card

print("Начало")

card = get_card("Swamp")

print("Конец")

if card:
    print(card.name)
