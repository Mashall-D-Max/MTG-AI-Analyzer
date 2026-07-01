class CompareAdvisor:
    """
    Генератор простых рекомендаций по замене карт.

    Берёт:
    - missing_cards: чего не хватает относительно эталона;
    - extra_cards: что лишнее относительно эталона.

    Возвращает список замен.
    """

    def build_recommendations(self, comparison):
        missing_cards = dict(comparison.get("missing_cards", {}))

        extra_cards = dict(comparison.get("extra_cards", {}))

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

                recommendations.append(
                    {
                        "remove": extra_card_name,
                        "add": missing_card_name,
                        "quantity": quantity,
                    }
                )

                extra_quantity -= quantity
                missing_quantity -= quantity

                extra_cards[extra_card_name] = extra_quantity
                missing_cards[missing_card_name] = missing_quantity

                if extra_quantity <= 0:
                    break

        return recommendations
