class Archetype:
    """
    Архетип колоды в конкретном формате.

    Например:
    Pioneer / Orzhov Ketramose
    Standard / Mono Red Aggro
    Modern / Boros Energy
    """

    def __init__(
        self,
        name,
        format_name,
        colors=None,
        tier=None,
        meta_share=0.0,
        win_rate=0.0,
    ):
        self.name = name
        self.format_name = format_name
        self.colors = colors or []
        self.tier = tier
        self.meta_share = meta_share
        self.win_rate = win_rate

    def __repr__(self):
        return (
            f"Archetype("
            f"name={self.name!r}, "
            f"format={self.format_name!r}, "
            f"tier={self.tier!r}, "
            f"meta_share={self.meta_share}, "
            f"win_rate={self.win_rate}"
            f")"
        )
