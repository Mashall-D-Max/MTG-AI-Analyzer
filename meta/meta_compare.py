class MetaCompare:
    """
    Сравнение пользовательской колоды с эталонной колодой архетипа.

    Поддерживает:
    - сравнение mainboard;
    - сравнение sideboard;
    - общий процент совпадения.
    """

    def compare_decks(self, user_deck, meta_deck):
        """
        Старый метод сохранён для совместимости.
        Сравнивает только mainboard.
        """

        user_cards = self._deck_to_dict(user_deck.cards)
        meta_cards = self._deck_to_dict(meta_deck.cards)

        return self._compare_card_dicts(
            user_cards=user_cards,
            meta_cards=meta_cards,
        )

    def compare_sideboards(self, user_deck, meta_deck):
        user_cards = self._deck_to_dict(user_deck.sideboard)
        meta_cards = self._deck_to_dict(meta_deck.sideboard)

        return self._compare_card_dicts(
            user_cards=user_cards,
            meta_cards=meta_cards,
        )

    def compare_all_zones(self, user_deck, meta_deck):
        """
        Полное сравнение колоды:

        - mainboard;
        - sideboard;
        - overall.
        """

        mainboard = self.compare_decks(
            user_deck=user_deck,
            meta_deck=meta_deck,
        )

        sideboard = self.compare_sideboards(
            user_deck=user_deck,
            meta_deck=meta_deck,
        )

        user_all_cards = self._deck_to_dict(user_deck.cards + user_deck.sideboard)

        meta_all_cards = self._deck_to_dict(meta_deck.cards + meta_deck.sideboard)

        overall = self._compare_card_dicts(
            user_cards=user_all_cards,
            meta_cards=meta_all_cards,
        )

        return {
            "mainboard": mainboard,
            "sideboard": sideboard,
            "overall": overall,
            "overall_similarity": overall["similarity"],
        }

    def _compare_card_dicts(self, user_cards, meta_cards):
        missing_cards = {}
        extra_cards = {}
        matched_cards = {}

        for card_name, meta_quantity in meta_cards.items():
            user_quantity = user_cards.get(card_name, 0)

            if user_quantity < meta_quantity:
                missing_cards[card_name] = meta_quantity - user_quantity

            if user_quantity > 0:
                matched_cards[card_name] = min(
                    user_quantity,
                    meta_quantity,
                )

        for card_name, user_quantity in user_cards.items():
            meta_quantity = meta_cards.get(card_name, 0)

            if user_quantity > meta_quantity:
                extra_cards[card_name] = user_quantity - meta_quantity

        similarity = self._calculate_similarity(
            user_cards=user_cards,
            meta_cards=meta_cards,
        )

        return {
            "similarity": similarity,
            "missing_cards": missing_cards,
            "extra_cards": extra_cards,
            "matched_cards": matched_cards,
        }

    def _deck_to_dict(self, deck_cards):
        result = {}

        for deck_card in deck_cards:
            card_name = deck_card.card.name

            result[card_name] = result.get(card_name, 0) + deck_card.quantity

        return result

    def _calculate_similarity(self, user_cards, meta_cards):
        if not meta_cards:
            return 0.0

        matched = 0
        total = sum(meta_cards.values())

        for card_name, meta_quantity in meta_cards.items():
            user_quantity = user_cards.get(card_name, 0)

            matched += min(
                user_quantity,
                meta_quantity,
            )

        return round(
            (matched / total) * 100,
            2,
        )
