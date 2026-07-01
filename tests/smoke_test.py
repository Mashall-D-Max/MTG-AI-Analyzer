import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))


from analyzer.deck_analyzer import DeckAnalyzer
from api.scryfall import get_card
from importers.deck_format import DeckFormat
from importers.format_detector import FormatDetector
from importers.import_manager import ImportManager
from parsers.deck_parser import load_deck
from parsers.decklist_parser import DecklistParser
from services.cache_service import cache

TEST_DECK_FILE = PROJECT_ROOT / "decks" / "test.txt"
TEST_ARENA_DECK_FILE = PROJECT_ROOT / "decks" / "arena_test.txt"


CLIPBOARD_DECK_TEXT = """
4 Fatal Push
4 Thoughtseize
4 Ketramose, the New Dawn
2 Plains
2 Swamp

Sideboard
2 Duress
"""


PARSER_TEST_TEXT = """
Deck
4 Fatal Push (MKM) 84
4 Thoughtseize (AKR) 127
4 Ketramose, the New Dawn (DFT) 17
2 Plains (DMU) 277
2 Swamp (DMU) 279

Sideboard
2 Duress (M21) 96
"""


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

    def test_deck_file_exists(self):

        if not TEST_DECK_FILE.exists():
            raise RuntimeError(f"Файл тестовой колоды не найден: {TEST_DECK_FILE}")

    def test_arena_deck_file_exists(self):

        if not TEST_ARENA_DECK_FILE.exists():
            raise RuntimeError(f"Файл Arena-колоды не найден: {TEST_ARENA_DECK_FILE}")

    def test_scryfall(self):

        card = get_card("Fatal Push")

        if card is None:
            raise RuntimeError("Scryfall не вернул карту")

        if card.name != "Fatal Push":
            raise RuntimeError(f"Ожидалась Fatal Push, получена {card.name}")

    def test_cache(self):

        card_name = "Fatal Push"

        if not cache.exists(card_name):

            card = get_card(card_name)

            if card is None:
                raise RuntimeError("Не удалось загрузить карту для проверки кэша")

        if not cache.exists(card_name):
            raise RuntimeError("Карта не появилась в кэше")

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

        if not isinstance(analysis["mana_curve"], dict):
            raise RuntimeError("mana_curve должен быть dict")

        if not isinstance(analysis["ai"], list):
            raise RuntimeError("ai должен быть list")

    def test_decklist_parser(self):

        deck = DecklistParser().parse_text(PARSER_TEST_TEXT)

        if deck.mainboard_size != 16:
            raise RuntimeError(
                f"Ожидалось 16 карт mainboard, получено {deck.mainboard_size}"
            )

        if deck.sideboard_size != 2:
            raise RuntimeError(
                f"Ожидалось 2 карты sideboard, получено {deck.sideboard_size}"
            )

        if deck.total_size != 18:
            raise RuntimeError(f"Ожидалось 18 карт всего, получено {deck.total_size}")

    def test_format_detector_txt(self):

        detected_format = FormatDetector.detect(TEST_DECK_FILE)

        if detected_format != DeckFormat.TXT:
            raise RuntimeError(f"Ожидался TXT, получен {detected_format}")

    def test_format_detector_arena(self):

        detected_format = FormatDetector.detect(TEST_ARENA_DECK_FILE)

        if detected_format != DeckFormat.ARENA:
            raise RuntimeError(f"Ожидался ARENA, получен {detected_format}")

    def test_format_detector_clipboard(self):

        detected_format = FormatDetector.detect(CLIPBOARD_DECK_TEXT)

        if detected_format != DeckFormat.CLIPBOARD:
            raise RuntimeError(f"Ожидался CLIPBOARD, получен {detected_format}")

    def test_format_detector_mtgdecks(self):

        url = "https://mtgdecks.net/Pioneer/example-decklist"

        detected_format = FormatDetector.detect(url)

        if detected_format != DeckFormat.MTGDECKS:
            raise RuntimeError(f"Ожидался MTGDECKS, получен {detected_format}")

    def test_import_manager_txt(self):

        deck = ImportManager().load(TEST_DECK_FILE)

        if deck.size <= 0:
            raise RuntimeError("ImportManager загрузил пустую TXT-колоду")

        if deck.unique_cards <= 0:
            raise RuntimeError("ImportManager не загрузил уникальные карты TXT")

        if deck.sideboard_size != 0:
            raise RuntimeError(
                f"У TXT-колоды не должно быть sideboard, получено {deck.sideboard_size}"
            )

    def test_import_manager_arena(self):

        deck = ImportManager().load(TEST_ARENA_DECK_FILE)

        if deck.mainboard_size != 16:
            raise RuntimeError(
                f"Ожидалось 16 карт mainboard, получено {deck.mainboard_size}"
            )

        if deck.sideboard_size != 2:
            raise RuntimeError(
                f"Ожидалось 2 карты sideboard, получено {deck.sideboard_size}"
            )

        if deck.total_size != 18:
            raise RuntimeError(f"Ожидалось 18 карт всего, получено {deck.total_size}")

    def test_import_manager_clipboard(self):

        deck = ImportManager().load(CLIPBOARD_DECK_TEXT)

        if deck.mainboard_size != 16:
            raise RuntimeError(
                f"Ожидалось 16 карт mainboard, получено {deck.mainboard_size}"
            )

        if deck.sideboard_size != 2:
            raise RuntimeError(
                f"Ожидалось 2 карты sideboard, получено {deck.sideboard_size}"
            )

        if deck.total_size != 18:
            raise RuntimeError(f"Ожидалось 18 карт всего, получено {deck.total_size}")

    def run(self):

        print("=" * 60)
        print("MTG AI Analyzer Smoke Test")
        print("=" * 60)
        print()

        self.run_check("Deck file exists", self.test_deck_file_exists)
        self.run_check("Arena deck file exists", self.test_arena_deck_file_exists)
        self.run_check("Scryfall card loading", self.test_scryfall)
        self.run_check("Cache", self.test_cache)
        self.run_check("Deck import", self.test_deck_import)
        self.run_check("Deck analyzer", self.test_deck_analyzer)
        self.run_check("Decklist parser", self.test_decklist_parser)
        self.run_check("Format detector TXT", self.test_format_detector_txt)
        self.run_check("Format detector Arena", self.test_format_detector_arena)
        self.run_check("Format detector Clipboard", self.test_format_detector_clipboard)
        self.run_check("Format detector MTGDecks", self.test_format_detector_mtgdecks)
        self.run_check("Import manager TXT", self.test_import_manager_txt)
        self.run_check(
            "Import manager Arena with sideboard",
            self.test_import_manager_arena,
        )
        self.run_check(
            "Import manager Clipboard with sideboard",
            self.test_import_manager_clipboard,
        )

        print()
        print("=" * 60)
        print(f"{self.passed} / {self.passed + self.failed} PASSED")
        print("=" * 60)

        if self.failed > 0:
            sys.exit(1)


if __name__ == "__main__":

    SmokeTest().run()
