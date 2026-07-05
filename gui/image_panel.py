import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image, ImageOps


class ImagePanel(ctk.CTkFrame):
    """
    Панель изображения карты с сохранением пропорций.
    """

    DISPLAY_SIZE = (250, 350)

    def __init__(self, master):
        super().__init__(master)

        self.current_image = None

        self.image_label = ctk.CTkLabel(
            self,
            text="Карта не загружена",
        )

        self.image_label.pack(
            expand=True,
            padx=10,
            pady=10,
        )

    def show_loading(self):
        self.current_image = None

        self.image_label.configure(
            image=None,
            text="Загрузка изображения...",
        )

        self.image_label.image = None

    def show_error(self, message="Изображение недоступно"):
        self.current_image = None

        self.image_label.configure(
            image=None,
            text=message,
        )

        self.image_label.image = None

    def show_image(self, pil_image):
        if pil_image is None:
            self.show_error()
            return

        try:
            resampling = Image.Resampling.LANCZOS
        except AttributeError:
            resampling = Image.LANCZOS

        prepared_image = ImageOps.contain(
            pil_image,
            self.DISPLAY_SIZE,
            method=resampling,
        )

        image = CTkImage(
            light_image=prepared_image,
            dark_image=prepared_image,
            size=prepared_image.size,
        )

        self.current_image = image

        self.image_label.configure(
            image=image,
            text="",
        )

        self.image_label.image = image
