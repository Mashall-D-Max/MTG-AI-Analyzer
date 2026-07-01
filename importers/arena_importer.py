from importers.base_importer import BaseImporter


class ArenaImporter(BaseImporter):
    """
    Импорт колоды в формате MTG Arena.
    """

    def load(self, filename):

        raise NotImplementedError
