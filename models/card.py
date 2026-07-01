class Card:
    """
    Модель карты Magic: The Gathering.
    """

    def __init__(self, data):

        self.name = data.get("name") or ""

        self.mana_cost = data.get("mana_cost") or ""

        self.type_line = data.get("type_line") or ""

        self.oracle_text = data.get("oracle_text") or ""

        self.rarity = data.get("rarity") or ""

        self.set_name = data.get("set_name") or ""

        self.artist = data.get("artist") or ""

        self.colors = data.get("colors") or []

        self.cmc = data.get("cmc") or 0

        self.prices = data.get("prices") or {}

        self.legalities = data.get("legalities") or {}

        self.image_uris = data.get("image_uris") or {}

    def show(self):

        print("=" * 60)
        print(self.name.upper())
        print("=" * 60)

        print(f"Стоимость маны : {self.mana_cost}")
        print(f"Тип            : {self.type_line}")
        print(f"Редкость       : {self.rarity}")
        print(f"Сет            : {self.set_name}")
        print(f"CMC            : {self.cmc}")
        print(
            f"Цвета          : "
            f"{', '.join(self.colors) if self.colors else 'Бесцветная'}"
        )

        print("\nOracle Text")
        print("-" * 60)
        print(self.oracle_text)

        print("\nЛегальность")
        print("-" * 60)

        for format_name in [
            "standard",
            "pioneer",
            "modern",
            "legacy",
            "commander",
        ]:
            status = self.legalities.get(format_name, "unknown")
            print(f"{format_name.capitalize():12}: {status}")

        print("\nЦены")
        print("-" * 60)
        print(f"USD : {self.prices.get('usd')}")
        print(f"EUR : {self.prices.get('eur')}")

        print("\nХудожник:", self.artist)
