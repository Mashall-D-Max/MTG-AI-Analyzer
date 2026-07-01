from providers.base_provider import BaseProvider


class MTGDecksProvider(BaseProvider):

    @property
    def name(self):

        return "MTGDecks"

    def get_meta(self, format_name):

        raise NotImplementedError

    def get_archetypes(self, format_name):

        raise NotImplementedError

    def get_deck(self, url):

        raise NotImplementedError
