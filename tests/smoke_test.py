import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))


from analyzer.deck_analyzer import DeckAnalyzer
from api.scryfall import get_card
from parsers.deck_parser import load_deck
from services.cache_service import cache

TEST_DECK_FILE = PROJECT_ROOT / "decks" / "test.txt"


class SmokeTest:

    def __init__(self):

        self.passed = 0
        self.failed = 0

    def run_check(self, name, func):

        try:

            func()

            self.passed += 1

            print(f"[ OK ] {name}")

        except Exception as error:

            self.failed += 1

            print(f"[FAIL] {name}")
            print(f"       {error}")

    def test_cache(self):

        card_name = "Fatal Push"

        if not cache.exists(card_name):

            card = get_card(card_name)

            if card is None:
                raise RuntimeError("Не удалось загрузить карту для проверки кэша")

        if not cache.exists(card_name):
            raise RuntimeError("Карта не появилась в кэше")

    def test_scryfall(self):

        card = get_card("Fatal Push")

        if card is None:
            raise RuntimeError("Scryfall не вернул карту")

        if card.name != "Fatal Push":
            raise RuntimeError("Загружена неправильная карта")

    def test_deck_file_exists(self):

        if not TEST_DECK_FILE.exists():
            raise RuntimeError(f"Файл колоды не найден: {TEST_DECK_FILE}")

    def test_deck_import(self):

        deck = load_deck(TEST_DECK_FILE)

        if deck.size <= 0:
            raise RuntimeError("Колода загрузилась пустой")

        if deck.unique_cards <= 0:
            raise RuntimeError("Не найдены уникальные карты")

    def test_deck_analyzer(self):

        deck = load_deck(TEST_DECK_FILE)

        analysis = DeckAnalyzer(deck).analyze()

        required_keys = [
            "size",
            "unique_cards",
            "mana_curve",
            "colors",
            "card_types",
            "mana_sources",
            "mana_requirements",
            "ai",
        ]

        for key in required_keys:

            if key not in analysis:
                raise RuntimeError(f"В анализе отсутствует ключ: {key}")

        if analysis["size"] <= 0:
            raise RuntimeError("Размер колоды равен 0")

    def run(self):

        print("=" * 60)
        print("MTG AI Analyzer Smoke Test")
        print("=" * 60)
        print()

        self.run_check("Deck file exists", self.test_deck_file_exists)
        self.run_check("Scryfall card loading", self.test_scryfall)
        self.run_check("Cache", self.test_cache)
        self.run_check("Deck import", self.test_deck_import)
        self.run_check("Deck analyzer", self.test_deck_analyzer)

        print()
        print("=" * 60)
        print(f"{self.passed} / {self.passed + self.failed} PASSED")
        print("=" * 60)

        if self.failed > 0:
            sys.exit(1)


if __name__ == "__main__":

    SmokeTest().run()
