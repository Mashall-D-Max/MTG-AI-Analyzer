from importers.deck_format import DeckFormat
from importers.format_detector import FormatDetector
from importers.import_manager import ImportManager
from importers.registry import registry

url = "https://mtgdecks.net/Pioneer/example-decklist"

detected_format = FormatDetector.detect(url)

print("=" * 60)
print("MTGDECKS IMPORTER TEST")
print("=" * 60)

print("Detected format:", detected_format)

if detected_format != DeckFormat.MTGDECKS:
    raise RuntimeError(f"Ожидался MTGDECKS, получен {detected_format}")

importer = registry.get(DeckFormat.MTGDECKS)

print("Importer:", importer)

if importer is None:
    raise RuntimeError("MTGDecksImporter не зарегистрирован")

manager = ImportManager()

print("ImportManager:", manager)

print()
print("RESULT: OK")
