import requests
from io import BytesIO
from PIL import Image

BASE_URL = "https://api.scryfall.com"


class ScryfallClient:

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": "MTG-AI-Analyzer/1.0 (GitHub: Mashall-D-Max)",
                "Accept": "application/json",
            }
        )

    def get_card(self, name):

        response = self.session.get(
            f"{BASE_URL}/cards/named", params={"exact": name}, timeout=20
        )

        response.raise_for_status()

        return response.json()

    def get_image(self, url):

        headers = {
            "User-Agent": "MTG-AI-Analyzer/1.0 (GitHub: Mashall-D-Max)",
            "Accept": "image/*",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        return Image.open(BytesIO(response.content))


client = ScryfallClient()
