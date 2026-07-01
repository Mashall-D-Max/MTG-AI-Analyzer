from importers.format_detector import FormatDetector
from importers.registry import registry

# Импортируем, чтобы зарегистрировать импортеры
import importers.txt_importer
import importers.arena_importer


class ImportManager:
    """
    Универсальный менеджер импорта.
    """

    def load(self, source):

        deck_format = FormatDetector.detect(source)

        importer = registry.get(deck_format)

        if importer is None:

            raise ValueError(f"Импортер для {deck_format.value} не зарегистрирован.")

        return importer.load(source)
