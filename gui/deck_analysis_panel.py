import customtkinter as ctk


class DeckAnalysisPanel(ctk.CTkFrame):
    """
    Панель отображения анализа колоды.
    """

    COLOR_NAMES = {
        "W": "White",
        "U": "Blue",
        "B": "Black",
        "R": "Red",
        "G": "Green",
    }

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self,
            text="Анализ колоды",
            font=("Arial", 18, "bold"),
        )
        self.title.pack(pady=10)

        self.text = ctk.CTkTextbox(
            self,
            width=420,
            height=500,
        )
        self.text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

    def show_analysis(self, analysis):
        self.text.delete("1.0", "end")

        self._write("=== Общая информация ===\n\n")

        self._write(
            f"Mainboard      : {analysis.get('mainboard_size', analysis.get('size', 0))}\n"
        )
        self._write(f"Sideboard      : {analysis.get('sideboard_size', 0)}\n")
        self._write(
            f"Всего карт     : {analysis.get('total_size', analysis.get('size', 0))}\n"
        )
        self._write(f"Уникальных     : {analysis.get('unique_cards', 0)}\n")

        self._write("\n=== Кривая маны ===\n\n")

        for cmc, count in analysis.get("mana_curve", {}).items():
            self._write(f"CMC {cmc}: {count}\n")

        self._write("\n=== Цвета карт ===\n\n")

        for color, count in analysis.get("colors", {}).items():
            color_name = self.COLOR_NAMES.get(color, color)
            self._write(f"{color_name}: {count}\n")

        self._write("\n=== Типы карт ===\n\n")

        for card_type, count in analysis.get("card_types", {}).items():
            self._write(f"{card_type}: {count}\n")

        self._write("\n=== Источники маны ===\n\n")

        for color, count in analysis.get("mana_sources", {}).items():
            color_name = self.COLOR_NAMES.get(color, color)
            self._write(f"{color_name}: {count}\n")

        self._write("\n=== Требования по мане ===\n\n")

        for color, count in analysis.get("mana_requirements", {}).items():
            color_name = self.COLOR_NAMES.get(color, color)
            self._write(f"{color_name}: {count}\n")

        self._write("\n=== AI Mana Analysis ===\n\n")

        for item in analysis.get("ai", []):
            status = "OK" if item["ok"] else "NOT ENOUGH"

            self._write(
                f"{status} {item['name']}: "
                f"{item['sources']}/{item['required']} "
                f"({item['difference']})\n"
            )

    def show_error(self, message):
        self.text.delete("1.0", "end")

        self._write("Ошибка анализа колоды\n\n")
        self._write(message)

    def _write(self, text):
        self.text.insert("end", text)
