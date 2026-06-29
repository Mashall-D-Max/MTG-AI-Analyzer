import customtkinter as ctk


class StatusBar(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, height=30)

        self.label = ctk.CTkLabel(self, text="Готово")

        self.label.pack(side="left", padx=10)
