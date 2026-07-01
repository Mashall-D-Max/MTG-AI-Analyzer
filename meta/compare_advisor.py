import re


class CompareAdvisor:
    """
    Генератор рекомендаций по замене карт.

    Дополнительно умеет оценивать изменение цветовых требований маны:
    например +1 W, -1 B.
    """

    COLORS = ("W", "U", "B", "R", "G")

    COLOR_SYMBOLS = {
        "W": "⚪",
        "U": "🔵",
        "B": "⚫",
        "R": "🔴",
        "G": "🟢",
    }

    MANA_TOKEN_PATTERN = re.compile(r"\{([^}]+)\}")

    def build_recommendations(
        self,
        comparison,
        user_deck_cards=None,
        reference_deck_cards=None,
    ):
        missing_cards = dict(comparison.get("missing_cards", {}))

        extra_cards = dict(comparison.get("extra_cards", {}))

        user_card_map = self._build_card_map(user_deck_cards)

        reference_card_map = self._build_card_map(reference_deck_cards)

        recommendations = []

        for extra_card_name in sorted(list(extra_cards.keys())):
            extra_quantity = extra_cards.get(extra_card_name, 0)

            if extra_quantity <= 0:
                continue

            for missing_card_name in sorted(list(missing_cards.keys())):
                missing_quantity = missing_cards.get(missing_card_name, 0)

                if missing_quantity <= 0:
                    continue

                quantity = min(
                    extra_quantity,
                    missing_quantity,
                )

                remove_card = user_card_map.get(extra_card_name)

                add_card = reference_card_map.get(missing_card_name)

                mana_change = self._build_mana_change(
                    remove_card=remove_card,
                    add_card=add_card,
                    quantity=quantity,
                )

                mana_delta = self._build_mana_delta(
                    remove_card=remove_card,
                    add_card=add_card,
                    quantity=quantity,
                )

                recommendations.append(
                    {
                        "remove": extra_card_name,
                        "add": missing_card_name,
                        "quantity": quantity,
                        "mana_change": mana_change,
                        "mana_delta": mana_delta,
                    }
                )

                extra_quantity -= quantity
                missing_quantity -= quantity

                extra_cards[extra_card_name] = extra_quantity
                missing_cards[missing_card_name] = missing_quantity

                if extra_quantity <= 0:
                    break

        return recommendations

    def _build_card_map(self, deck_cards):
        result = {}

        if not deck_cards:
            return result

        for deck_card in deck_cards:
            card = deck_card.card

            if card.name not in result:
                result[card.name] = card

        return result

    def _build_mana_change(
        self,
        remove_card,
        add_card,
        quantity,
    ):
        if remove_card is None or add_card is None:
            return "мана: нет данных"

        mana_delta = self._build_mana_delta(
            remove_card=remove_card,
            add_card=add_card,
            quantity=quantity,
        )

        parts = []

        for color in self.COLORS:
            value = mana_delta.get(color, 0)

            if value == 0:
                continue

            sign = "+" if value > 0 else ""

            parts.append(f"{sign}{value} {self.COLOR_SYMBOLS[color]}")

        if not parts:
            return "мана: без изменений"

        return "мана: " + ", ".join(parts)

    def _build_mana_delta(
        self,
        remove_card,
        add_card,
        quantity,
    ):
        delta = {color: 0 for color in self.COLORS}

        if remove_card is None or add_card is None:
            return delta

        remove_pips = self._count_colored_pips(remove_card.mana_cost)

        add_pips = self._count_colored_pips(add_card.mana_cost)

        for color in self.COLORS:
            delta[color] = (
                add_pips.get(color, 0) - remove_pips.get(color, 0)
            ) * quantity

        return delta

    def _count_colored_pips(self, mana_cost):
        result = {color: 0 for color in self.COLORS}

        if not mana_cost:
            return result

        tokens = self.MANA_TOKEN_PATTERN.findall(str(mana_cost))

        for token in tokens:
            token = token.upper()

            for color in self.COLORS:
                if color in token:
                    result[color] += 1

        return result
