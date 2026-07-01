from analyzer.mana_base import ManaBaseAnalyzer
from analyzer.mana_requirements import ManaRequirementsAnalyzer
from meta.compare_advisor import CompareAdvisor


class ManaImpactAdvisor:
    """
    Проверяет, хватает ли текущей манабазы после рекомендованных замен.

    Логика:
    - берём текущие источники маны из пользовательской колоды;
    - берём текущие требования по мане;
    - применяем изменения от рекомендаций;
    - показываем, хватает ли источников.
    """

    COLORS = ("W", "U", "B", "R", "G")

    COLOR_NAMES = {
        "W": "White",
        "U": "Blue",
        "B": "Black",
        "R": "Red",
        "G": "Green",
    }

    COLOR_SYMBOLS = {
        "W": "⚪",
        "U": "🔵",
        "B": "⚫",
        "R": "🔴",
        "G": "🟢",
    }

    def analyze(
        self,
        user_deck,
        comparison,
        user_deck_cards,
        reference_deck_cards,
    ):
        mana_sources = ManaBaseAnalyzer(user_deck).analyze()

        current_requirements = ManaRequirementsAnalyzer(user_deck).analyze()

        recommendations = CompareAdvisor().build_recommendations(
            comparison=comparison,
            user_deck_cards=user_deck_cards,
            reference_deck_cards=reference_deck_cards,
        )

        adjusted_requirements = dict(current_requirements)

        for recommendation in recommendations:
            mana_delta = recommendation.get("mana_delta", {})

            for color, value in mana_delta.items():
                adjusted_requirements[color] = (
                    adjusted_requirements.get(color, 0) + value
                )

                if adjusted_requirements[color] < 0:
                    adjusted_requirements[color] = 0

        result = []

        for color in self.COLORS:
            required = adjusted_requirements.get(color, 0)
            sources = mana_sources.get(color, 0)

            if required == 0 and sources == 0:
                continue

            difference = sources - required

            result.append(
                {
                    "color": color,
                    "name": self.COLOR_NAMES[color],
                    "symbol": self.COLOR_SYMBOLS[color],
                    "sources": sources,
                    "required": required,
                    "difference": difference,
                    "ok": difference >= 0,
                }
            )

        return result
