from datetime import datetime


class MetaSnapshot:
    """
    Снимок меты на конкретную дату.

    Например:
    Pioneer, 2026-07-01:
    - Rakdos Midrange 12%
    - Orzhov Ketramose 9%
    - Izzet Phoenix 8%
    """

    def __init__(self, format_name, source_name, date=None):
        self.format_name = format_name
        self.source_name = source_name
        self.date = date or datetime.now()
        self.archetypes = []

    def add_archetype(self, archetype):
        self.archetypes.append(archetype)

    @property
    def count(self):
        return len(self.archetypes)

    def top_archetypes(self, limit=10):
        return sorted(
            self.archetypes,
            key=lambda archetype: archetype.meta_share,
            reverse=True,
        )[:limit]

    def find_archetype(self, name):
        name_lower = name.lower()

        for archetype in self.archetypes:
            if archetype.name.lower() == name_lower:
                return archetype

        return None
