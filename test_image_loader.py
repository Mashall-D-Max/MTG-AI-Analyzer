from api.scryfall import get_card
from services.image_service import load_card_image

card = get_card("Fatal Push")

if card is None:
    raise RuntimeError("Карта не загружена")

print("Card:", card.name)
print("Image URIs:", card.image_uris)

image = load_card_image(card)

if image is None:
    raise RuntimeError("Изображение не загружено")

print("Image:", image)
print("Size:", image.size)
print("Mode:", image.mode)

print("RESULT: OK")
