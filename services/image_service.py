from api.client import client


def load_card_image(card):

    if not card.image_uris:
        return None

    url = card.image_uris.get("normal")

    if not url:
        return None

    try:

        return client.get_image(url)

    except Exception as e:

        print("Ошибка загрузки изображения:", e)

        return None
