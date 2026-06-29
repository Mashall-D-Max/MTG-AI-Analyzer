from api.client import ScryfallClient
from models.card import Card

client = ScryfallClient()


def get_card(card_name):

    try:

        data = client.get_card(card_name)

        return Card(data)

    except Exception as e:

        print("Ошибка Scryfall:", e)

        return None
