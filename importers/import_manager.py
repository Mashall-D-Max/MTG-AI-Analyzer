from importers.format_detector import FormatDetector
from importers.registry import registry

# Импортируем модули, чтобы они зарегистрировали свои импортеры.
import importers.txt_importer
import importers.arena_importer


class ImportManager:
    """
    Универсальный менеджер импорта колод.
    """

    def load(self, source):

        deck_format = FormatDetector.detect(source)

        importer = registry.get(deck_format)

        if importer is None:
            raise ValueError(
                f"Импортер для формата '{deck_format.value}' не зарегистрирован."
            )

        return importer.load(source)
