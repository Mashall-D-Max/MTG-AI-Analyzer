from api.client import client
from utils.logger import logger


def load_card_image(card):
    """
    Получить изображение карты.

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
        return client.get_image(image_url)

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
