import requests
from PIL import Image
from io import BytesIO

url = "https://cards.scryfall.io/normal/front/c/f/cffae8d0-7b4e-42ed-8124-24a86b38f490.jpg?1738356679"

headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers, timeout=30)

    print("HTTP:", response.status_code)

    image = Image.open(BytesIO(response.content))

    print("Размер:", image.size)

except Exception as e:
    print(type(e).__name__)
    print(e)
