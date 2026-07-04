from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from services.scryfall_thumbnail_service import (
    ScryfallThumbnailService,
)


class FakeImageResponse:
    def __init__(
        self,
        image_content,
    ):
        self.status_code = 200
        self.content = image_content


class FakeImageSession:
    def __init__(
        self,
        image_content,
    ):
        self.image_content = image_content
        self.calls = []

    def get(
        self,
        url,
        headers=None,
        timeout=None,
    ):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "timeout": timeout,
            }
        )

        return FakeImageResponse(self.image_content)


def create_test_image_bytes():
    image = Image.new(
        "RGB",
        (100, 140),
        (120, 120, 120),
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()


print("=" * 60)
print("SCRYFALL THUMBNAIL SERVICE TEST")
print("=" * 60)


image_content = create_test_image_bytes()

session = FakeImageSession(image_content=image_content)


with TemporaryDirectory() as temporary_directory:
    service = ScryfallThumbnailService(
        cache_directory=temporary_directory,
        session=session,
        timeout=5,
    )

    card_data = {
        "id": "test-card-id",
        "name": "Aang, Swift Savior",
        "set": "tla",
        "collector_number": "1",
        "lang": "en",
        "image_uris": {
            "small": ("https://cards.scryfall.io/" "small/test-card.jpg"),
        },
    }

    first_image = service.load_thumbnail(
        card_data=card_data,
        size=(120, 168),
    )

    if first_image.size != (120, 168):
        raise RuntimeError("Миниатюра получила неверный размер: " f"{first_image.size}")

    if len(session.calls) != 1:
        raise RuntimeError("При первой загрузке ожидался " "один сетевой запрос")

    cache_path = service.get_cache_path(card_data)

    if not cache_path.exists():
        raise RuntimeError("Файл миниатюры не создан в кэше")

    second_image = service.load_thumbnail(
        card_data=card_data,
        size=(60, 84),
    )

    if second_image.size != (60, 84):
        raise RuntimeError("Изображение из кэша получило " "неверный размер")

    if len(session.calls) != 1:
        raise RuntimeError("При повторной загрузке произошёл " "лишний сетевой запрос")

    double_faced_card = {
        "id": "double-faced-card",
        "name": "Test Front // Test Back",
        "card_faces": [
            {
                "name": "Test Front",
                "image_uris": {
                    "normal": ("https://cards.scryfall.io/" "normal/test-front.jpg"),
                },
            },
            {
                "name": "Test Back",
                "image_uris": {
                    "normal": ("https://cards.scryfall.io/" "normal/test-back.jpg"),
                },
            },
        ],
    }

    double_faced_url = service.get_image_url(double_faced_card)

    expected_url = "https://cards.scryfall.io/" "normal/test-front.jpg"

    if double_faced_url != expected_url:
        raise RuntimeError("Для двухсторонней карты выбрана " "неверная сторона")

    removed_files = service.clear_cache()

    if removed_files != 1:
        raise RuntimeError(
            "Очистка кэша удалила неверное " f"количество файлов: {removed_files}"
        )

    if Path(cache_path).exists():
        raise RuntimeError("Файл остался после очистки кэша")


print("Network requests:", len(session.calls))
print("Cache:", cache_path)
print("Front face URL:", double_faced_url)

print()
print("RESULT: OK")
