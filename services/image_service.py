import requests
from PIL import Image
from io import BytesIO

HEADERS = {"User-Agent": "Mozilla/5.0"}


def load_card_image(card):

    url = card.image_uris["normal"]

    print("URL:", url)

    response = requests.get(url, headers=HEADERS, timeout=30, stream=True)

    print("HTTP:", response.status_code)

    image = Image.open(BytesIO(response.content))

    print("IMAGE:", image.size)

    return image
