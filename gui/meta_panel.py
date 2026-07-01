import customtkinter as ctk

from utils.text_shortcuts import bind_text_shortcuts


class MetaPanel(ctk.CTkFrame):
    """
    Панель отображения меты и сравнения колод.
    """

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self,
            text="Мета / Compare",
            font=("Arial", 18, "bold"),
        )
        self.title.pack(pady=10)

        self.text = ctk.CTkTextbox(
            self,
            width=360,
            height=500,
        )
        self.text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        bind_text_shortcuts(self.text)

    def show_snapshot(self, snapshot):
        self.text.delete("1.0", "end")

        self._write("=== Meta Snapshot ===\n\n")
        self._write(f"Format : {snapshot.format_name}\n")
        self._write(f"Source : {snapshot.source_name}\n")
        self._write(f"Count  : {snapshot.count}\n\n")

        self._write("=== Top Archetypes ===\n\n")

        if snapshot.count == 0:
            self._write("Архетипы не найдены.\n")
            return

        for archetype in snapshot.top_archetypes(15):
            self._write(f"{archetype.name} | " f"{archetype.meta_share}%")

            if archetype.win_rate:
                self._write(f" | WR {archetype.win_rate}%")

            if archetype.tier:
                self._write(f" | {archetype.tier}")

            self._write("\n")

    def show_compare_result(
        self,
        comparison,
        user_deck=None,
        reference_deck=None,
    ):
        self.text.delete("1.0", "end")

        similarity = comparison.get("similarity", 0)

        missing_cards = comparison.get("missing_cards", {})
        extra_cards = comparison.get("extra_cards", {})
        matched_cards = comparison.get("matched_cards", {})

        self._write("=== Meta Compare ===\n\n")

        self._write("Сравнение пока выполняется только по mainboard.\n\n")

        if user_deck is not None:
            self._write(f"Твоя колода       : {user_deck.mainboard_size} карт\n")

        if reference_deck is not None:
            self._write(f"Эталонная колода  : {reference_deck.mainboard_size} карт\n")

        self._write("\n")

        self._write(f"Совпадение: {similarity}%\n")

        self._write("\n=== Не хватает ===\n\n")

        if not missing_cards:
            self._write("Ничего не не хватает.\n")
        else:
            for card_name, quantity in sorted(missing_cards.items()):
                self._write(f"{quantity} {card_name}\n")

        self._write("\n=== Лишние карты ===\n\n")

        if not extra_cards:
            self._write("Лишних карт нет.\n")
        else:
            for card_name, quantity in sorted(extra_cards.items()):
                self._write(f"{quantity} {card_name}\n")

        self._write("\n=== Совпало ===\n\n")

        if not matched_cards:
            self._write("Совпадений нет.\n")
        else:
            for card_name, quantity in sorted(matched_cards.items()):
                self._write(f"{quantity} {card_name}\n")

    def show_loading(self, format_name):
        self.text.delete("1.0", "end")

        self._write("Загрузка меты...\n\n")
        self._write(f"Формат: {format_name}\n")

    def show_compare_loading(self):
        self.text.delete("1.0", "end")

        self._write("Сравнение колод...\n\n")
        self._write("Загружаю эталонную колоду с MTGDecks и сравниваю с текущей.\n")

    def show_error(self, message):
        self.text.delete("1.0", "end")

        self._write("Ошибка\n\n")
        self._write(str(message))

    def clear(self):
        self.text.delete("1.0", "end")

    def _write(self, text):
        self.text.insert("end", text)
