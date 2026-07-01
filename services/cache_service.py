import json

from config import CARD_CACHE_DIR


class CacheService:
    """
    Работа с локальным кэшем карт.
    """

    def __init__(self):

        CARD_CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _filename(self, card_name):

        safe_name = card_name.replace("/", "_").replace("\\", "_").replace(":", "_")

        return CARD_CACHE_DIR / f"{safe_name}.json"

    def exists(self, card_name):

        return self._filename(card_name).exists()

    def load(self, card_name):

        filename = self._filename(card_name)

        with open(
            filename,
            encoding="utf-8",
        ) as file:

            return json.load(file)

    def save(self, card_name, data):

        filename = self._filename(card_name)

        with open(
            filename,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )


cache = CacheService()
