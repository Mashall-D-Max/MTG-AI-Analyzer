from analyzer.mana_curve import ManaCurve
from analyzer.colors import ColorAnalyzer
from analyzer.card_types import CardTypeAnalyzer
from analyzer.mana_base import ManaBaseAnalyzer
from analyzer.mana_requirements import ManaRequirementsAnalyzer
from analyzer.ai_mana import AIManaAnalyzer


class DeckAnalyzer:
    """
    Главный анализатор колоды.
    Собирает результаты всех специализированных анализаторов.
    """

    def __init__(self, deck):
        self.deck = deck

    def analyze(self):
        mana_curve = ManaCurve(self.deck).calculate()
        colors = ColorAnalyzer(self.deck).calculate()
        card_types = CardTypeAnalyzer(self.deck).calculate()
        mana_sources = ManaBaseAnalyzer(self.deck).analyze()
        mana_requirements = ManaRequirementsAnalyzer(self.deck).analyze()

        ai = AIManaAnalyzer().analyze(
            mana_sources,
            mana_requirements,
        )

        return {
            "size": self.deck.size,
            "mainboard_size": self.deck.mainboard_size,
            "sideboard_size": self.deck.sideboard_size,
            "total_size": self.deck.total_size,
            "unique_cards": self.deck.unique_cards,
            "unique_sideboard_cards": self.deck.unique_sideboard_cards,
            "mana_curve": mana_curve,
            "colors": colors,
            "card_types": card_types,
            "mana_sources": mana_sources,
            "mana_requirements": mana_requirements,
            "ai": ai,
        }
