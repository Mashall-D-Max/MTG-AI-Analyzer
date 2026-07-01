from meta.compare_advisor import CompareAdvisor


class DeckUpgradeBuilder:
    """
    Формирует текст обновлённой колоды на основе рекомендаций CompareAdvisor.
    """

    def build_upgraded_deck_text(
        self,
        user_deck,
        reference_deck,
        comparison,
    ):
        if "mainboard" in comparison:
            mainboard_comparison = comparison.get("mainboard", {})
            sideboard_comparison = comparison.get("sideboard", {})
        else:
            mainboard_comparison = comparison
            sideboard_comparison = {}

        upgraded_mainboard = self._apply_recommendations_to_zone(
            user_zone_cards=user_deck.cards,
            reference_zone_cards=reference_deck.cards,
            comparison=mainboard_comparison,
        )

        upgraded_sideboard = self._apply_recommendations_to_zone(
            user_zone_cards=user_deck.sideboard,
            reference_zone_cards=reference_deck.sideboard,
            comparison=sideboard_comparison,
        )

        return self._build_deck_text(
            mainboard=upgraded_mainboard,
            sideboard=upgraded_sideboard,
        )

    def _apply_recommendations_to_zone(
        self,
        user_zone_cards,
        reference_zone_cards,
        comparison,
    ):
        card_quantities = self._zone_to_dict(user_zone_cards)

        recommendations = CompareAdvisor().build_recommendations(
            comparison=comparison,
            user_deck_cards=user_zone_cards,
            reference_deck_cards=reference_zone_cards,
        )

        for recommendation in recommendations:
            remove_name = recommendation["remove"]
            add_name = recommendation["add"]
            quantity = recommendation["quantity"]

            card_quantities[remove_name] = (
                card_quantities.get(remove_name, 0) - quantity
            )

            if card_quantities.get(remove_name, 0) <= 0:
                card_quantities.pop(remove_name, None)

            card_quantities[add_name] = card_quantities.get(add_name, 0) + quantity

        return card_quantities

    def _zone_to_dict(self, deck_cards):
        result = {}

        for deck_card in deck_cards:
            card_name = deck_card.card.name

            result[card_name] = result.get(card_name, 0) + deck_card.quantity

        return result

    def _build_deck_text(self, mainboard, sideboard):
        lines = ["Deck"]

        for card_name, quantity in sorted(mainboard.items()):
            lines.append(f"{quantity} {card_name}")

        if sideboard:
            lines.append("")
            lines.append("Sideboard")

            for card_name, quantity in sorted(sideboard.items()):
                lines.append(f"{quantity} {card_name}")

        return "\n".join(lines)
