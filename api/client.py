import time
from io import BytesIO

import requests
from PIL import Image

from config import (
    IMAGE_TIMEOUT,
    REQUEST_TIMEOUT,
    SCRYFALL_API,
    USER_AGENT,
)


class ScryfallClient:

    RETRY_COUNT = 3
    RETRY_DELAY = 1

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            }
        )

    def get_card(self, name):

        url = f"{SCRYFALL_API}/cards/named"

        for attempt in range(self.RETRY_COUNT):

            try:

                response = self.session.get(
                    url,
                    params={"exact": name},
                    timeout=REQUEST_TIMEOUT,
                )

                response.raise_for_status()

                return response.json()

            except requests.RequestException:

                print(f"[{attempt + 1}/{self.RETRY_COUNT}] " f"Ошибка загрузки {name}")

                if attempt < self.RETRY_COUNT - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise

    def get_image(self, url):

        for attempt in range(self.RETRY_COUNT):

            try:

                response = requests.get(
                    url,
                    timeout=IMAGE_TIMEOUT,
                )

                response.raise_for_status()

                return Image.open(BytesIO(response.content))

            except requests.RequestException:

                print(
                    f"[{attempt + 1}/{self.RETRY_COUNT}] " "Ошибка загрузки изображения"
                )

                if attempt < self.RETRY_COUNT - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise


client = ScryfallClient()
