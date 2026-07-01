class ImportRegistry:
    """
    Реестр всех импортеров.
    """

    def __init__(self):

        self._importers = {}

    def register(self, deck_format, importer):

        self._importers[deck_format] = importer

    def get(self, deck_format):

        return self._importers.get(deck_format)

    def registered_formats(self):

        return list(self._importers.keys())


registry = ImportRegistry()
