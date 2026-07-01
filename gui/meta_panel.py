import customtkinter as ctk
from utils.text_shortcuts import bind_text_shortcuts


class MetaPanel(ctk.CTkFrame):
    """
    Панель отображения меты формата.
    """

    def __init__(self, master):
        super().__init__(master)

        self.title = ctk.CTkLabel(
            self,
            text="Мета",
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

        # Подключаем горячие клавиши
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

    def show_loading(self, format_name):
        self.text.delete("1.0", "end")

        self._write("Загрузка меты...\n\n")
        self._write(f"Формат: {format_name}\n")

    def show_error(self, message):
        self.text.delete("1.0", "end")

        self._write("Ошибка загрузки меты\n\n")
        self._write(str(message))

    def clear(self):
        self.text.delete("1.0", "end")

    def _write(self, text):
        self.text.insert("end", text)
