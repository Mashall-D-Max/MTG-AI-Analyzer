from api.client import client
from models.card import Card
from services.cache_service import cache
from utils.logger import logger


def get_card(card_name):
    """
    Получить карту из локального кэша или Scryfall.
    """

    # Проверяем кэш
    if cache.exists(card_name):

        logger.info(f"Cache hit: {card_name}")

        data = cache.load(card_name)

        return Card(data)

    try:

        logger.info(f"Downloading: {card_name}")

        data = client.get_card(card_name)

        cache.save(card_name, data)

        logger.info(f"Cached: {card_name}")

        return Card(data)

    except Exception:

        logger.exception(f"Failed to load card: {card_name}")

        return None
