class DeckAnalyzer:

    def __init__(self, deck):
        self.deck = deck

    def summary(self):

        print("=" * 50)
        print("АНАЛИЗ КОЛОДЫ")
        print("=" * 50)

        print(f"Размер колоды : {self.deck.size}")
        print(f"Земель        : {len(self.deck.lands)}")
        print(f"Существ       : {len(self.deck.creatures)}")
        print(f"Заклинаний    : {len(self.deck.spells)}")
