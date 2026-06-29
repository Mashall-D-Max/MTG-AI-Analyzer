class Card:

    def __init__(self, data):

        self.name = data.get("name")
        self.mana_cost = data.get("mana_cost")
        self.type_line = data.get("type_line")
        self.oracle_text = data.get("oracle_text")
        self.rarity = data.get("rarity")
        self.set_name = data.get("set_name")
        self.artist = data.get("artist")

        self.colors = data.get("colors", [])
        self.cmc = data.get("cmc")

        self.prices = data.get("prices", {})
        self.legalities = data.get("legalities", {})

        self.image_uris = data.get("image_uris", {})

    def show(self):

        print("=" * 60)
        print(self.name.upper())
        print("=" * 60)

        print(f"Стоимость маны : {self.mana_cost}")
        print(f"Тип            : {self.type_line}")
        print(f"Редкость       : {self.rarity}")
        print(f"Сет            : {self.set_name}")
        print(f"CMC            : {self.cmc}")
        print(f"Цвета          : {', '.join(self.colors) if self.colors else 'Бесцветная'}")

        print("\nOracle Text")
        print("-" * 60)
        print(self.oracle_text)

        print("\nЛегальность")
        print("-" * 60)

        for format_name in ["standard", "pioneer", "modern", "legacy", "commander"]:
            status = self.legalities.get(format_name, "unknown")
            print(f"{format_name.capitalize():12}: {status}")

        print("\nЦены")
        print("-" * 60)
        print(f"USD : {self.prices.get('usd')}")
        print(f"EUR : {self.prices.get('eur')}")

        print("\nХудожник:", self.artist)