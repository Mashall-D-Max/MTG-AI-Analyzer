from models.card import Card
import requests

BASE_URL = "https://api.scryfall.com"

HEADERS = {
    "User-Agent": "MTG-AI-Analyzer/1.0 (Learning Project)",
    "Accept": "application/json",
}


def get_card(card_name):
    """
    Получить информацию о карте по точному названию.
    """

    response = requests.get(
        f"{BASE_URL}/cards/named", params={"exact": card_name}, headers=HEADERS
    )

    if response.status_code == 200:

        data = response.json()

        print("=" * 60)
        print("КЛЮЧИ JSON")
        print(data.keys())
        print("=" * 60)

        print("IMAGE_URIS")
        print(data.get("image_uris"))
        print("=" * 60)

        return Card(data)

    print("Ошибка:", response.status_code)
    return None
