import customtkinter as ctk


class DeckAnalysisPanel(ctk.CTkFrame):

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
            width=400,
            height=300,
        )

        self.text.pack(fill="both", expand=True, padx=10, pady=10)

    def show_analysis(self, analysis):

        self.text.delete("1.0", "end")

        self.text.insert("end", "=== Общая информация ===\n\n")

        self.text.insert("end", f"Карт: {analysis['size']}\n")

        self.text.insert("end", f"Уникальных: {analysis['unique_cards']}\n\n")

        self.text.insert("end", "=== Кривая маны ===\n")

        for cmc in sorted(analysis["mana_curve"]):

            self.text.insert(
                "end",
                f"CMC {cmc}: {analysis['mana_curve'][cmc]}\n",
            )

        self.text.insert("\nend", "\n=== AI ===\n")

        for item in analysis["ai"]:

            status = "OK" if item["ok"] else "⚠"

            self.text.insert(
                "end",
                f"{status} {item['name']} : " f"{item['sources']}/{item['required']}\n",
            )
