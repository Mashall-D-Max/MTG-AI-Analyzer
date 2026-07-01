class TournamentResult:
    """
    Результат турнира.

    В будущем сюда будут попадать данные с MTGDecks:
    название турнира, формат, дата, количество игроков,
    топовые колоды и архетипы.
    """

    def __init__(
        self,
        name,
        format_name,
        date=None,
        players_count=0,
        source_name=None,
        url=None,
    ):
        self.name = name
        self.format_name = format_name
        self.date = date
        self.players_count = players_count
        self.source_name = source_name
        self.url = url
        self.decks = []

    def add_deck(self, deck):
        self.decks.append(deck)

    @property
    def deck_count(self):
        return len(self.decks)
