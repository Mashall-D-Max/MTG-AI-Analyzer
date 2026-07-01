from api.scryfall import get_card
from services.image_service import load_card_image
from services.image_cache_service import image_cache

card = get_card("Fatal Push")

if card is None:
    raise RuntimeError("Карта не загружена")

print("=" * 60)
print("IMAGE LOADER TEST")
print("=" * 60)

print("Card:", card.name)
print("Image URIs:", card.image_uris)

image_url = card.image_uris.get("normal")

if not image_url:
    raise RuntimeError("У карты нет normal image URL")

print()
print("Before load")
print("Cache exists:", image_cache.exists(image_url))

image = load_card_image(card)

if image is None:
    raise RuntimeError("Изображение не загружено")

print()
print("After load")
print("Cache exists:", image_cache.exists(image_url))

if not image_cache.exists(image_url):
    raise RuntimeError("Изображение не сохранилось в кэш")

cached_image = image_cache.load(image_url)

if cached_image is None:
    raise RuntimeError("Изображение не загрузилось из кэша")

print()
print("Image:", image)
print("Size:", image.size)
print("Mode:", image.mode)

print()
print("Cached image:", cached_image)
print("Cached size:", cached_image.size)
print("Cached mode:", cached_image.mode)

print()
print("RESULT: OK")
