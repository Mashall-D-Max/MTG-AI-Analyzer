from api.client import client
from services.image_cache_service import image_cache
from utils.logger import logger


def load_card_image(card):
    """
    Получить изображение карты.

    Приоритет:
    1. Найти URL изображения.
    2. Проверить локальный кэш.
    3. Если в кэше нет — скачать.
    4. Сохранить в кэш.
    5. Вернуть изображение в GUI.

    Поддерживает:
    - обычные карты с image_uris;
    - двухсторонние карты через card_faces;
    - fallback normal -> large -> small.
    """

    image_url = _get_best_image_url(card)

    if not image_url:
        logger.warning(f"У карты нет доступного изображения: {card.name}")
        return None

    try:
        if image_cache.exists(image_url):
            logger.info(f"Image cache hit: {card.name}")

            return image_cache.load(image_url)

        logger.info(f"Downloading image: {card.name}")

        image = client.get_image(image_url)

        if image is None:
            return None

        image_cache.save(
            image_url,
            image,
        )

        logger.info(f"Image cached: {card.name}")

        return image

    except Exception as error:
        logger.warning(f"Не удалось загрузить изображение {card.name}: {error}")

        return None


def _get_best_image_url(card):
    image_uris = card.image_uris or {}

    for size in ["normal", "large", "small"]:
        url = image_uris.get(size)

        if url:
            return url

    card_faces = getattr(card, "card_faces", []) or []

    for face in card_faces:
        face_image_uris = face.get("image_uris") or {}

        for size in ["normal", "large", "small"]:
            url = face_image_uris.get(size)

            if url:
                return url

    return None
