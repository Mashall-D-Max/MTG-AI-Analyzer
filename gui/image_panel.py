import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage


class ImagePanel(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.image_label = ctk.CTkLabel(self, text="Карта не загружена")

        self.image_label.pack(expand=True, padx=10, pady=10)

    def show_image(self, pil_image):

        if pil_image is None:
            self.image_label.configure(text="Изображение недоступно")
            return

        pil_image = pil_image.resize((250, 350))

        image = CTkImage(light_image=pil_image, dark_image=pil_image, size=(250, 350))

        self.image_label.configure(image=image, text="")

        # Важно! Иначе изображение удалит сборщик мусора Python
        self.image_label.image = image
