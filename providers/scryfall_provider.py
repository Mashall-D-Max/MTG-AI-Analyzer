from providers.base_provider import BaseProvider

from api.client import client


class ScryfallProvider(BaseProvider):

    @property
    def name(self):

        return "Scryfall"

    def get_card(self, card_name):

        return client.get_card(card_name)
