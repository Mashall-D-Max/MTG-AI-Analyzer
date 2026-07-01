import hashlib

from PIL import Image

from config import IMAGE_CACHE_DIR


class ImageCacheService:
    """
    Локальный кэш изображений карт.

    Ключом является URL изображения.
    Файл сохраняется как PNG, чтобы не зависеть от исходного расширения.
    """

    def __init__(self):
        IMAGE_CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _filename(self, image_url):
        url_hash = hashlib.sha256(str(image_url).encode("utf-8")).hexdigest()

        return IMAGE_CACHE_DIR / f"{url_hash}.png"

    def exists(self, image_url):
        return self._filename(image_url).exists()

    def load(self, image_url):
        filename = self._filename(image_url)

        image = Image.open(filename)

        return image.convert("RGB")

    def save(self, image_url, image):
        filename = self._filename(image_url)

        image.convert("RGB").save(
            filename,
            format="PNG",
        )


image_cache = ImageCacheService()
