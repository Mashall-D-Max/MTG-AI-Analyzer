import customtkinter as ctk

from services.deck_format_validator import DeckFormatValidator
from services.deck_save_service import DeckSaveService
from utils.text_shortcuts import bind_text_shortcuts


class DeckSaveDialog(ctk.CTkToplevel):
    """
    Диалог сохранения текущей колоды.

    Пользователь задаёт:
    - наименование колоды;
    - игровой формат;
    - формат экспортируемого файла;
    - допускается ли сохранение незавершённого черновика.
    """

    def __init__(
        self,
        master,
        deck,
        default_name="Новая колода",
        default_game_format=DeckFormatValidator.NO_FORMAT,
        default_export_format="Arena TXT",
        on_save_internal=None,
        on_save_as=None,
    ):
        super().__init__(master)

        self.deck = deck
        self.on_save_internal = on_save_internal
        self.on_save_as = on_save_as

        self.title("Сохранение колоды")
        self.geometry("760x650")
        self.minsize(700, 600)
        self.transient(master.winfo_toplevel())

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Сохранить колоду",
            font=("Arial", 24, "bold"),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(20, 10),
        )

        form = ctk.CTkFrame(self)
        form.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20,
            pady=10,
        )
        form.grid_columnconfigure(1, weight=1)

        name_label = ctk.CTkLabel(
            form,
            text="Наименование:",
            anchor="w",
            width=170,
        )
        name_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=12,
            pady=10,
        )

        self.name_entry = ctk.CTkEntry(
            form,
            placeholder_text="Например: Azorius Flash",
        )
        self.name_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=12,
            pady=10,
        )
        self.name_entry.insert(
            0,
            str(default_name or "Новая колода"),
        )
        bind_text_shortcuts(self.name_entry)

        game_format_label = ctk.CTkLabel(
            form,
            text="Игровой формат:",
            anchor="w",
            width=170,
        )
        game_format_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=12,
            pady=10,
        )

        self.game_format_combo = ctk.CTkComboBox(
            form,
            values=DeckFormatValidator.available_formats(),
            state="readonly",
            command=lambda value: self.refresh_validation(),
        )
        self.game_format_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=12,
            pady=10,
        )

        available_formats = DeckFormatValidator.available_formats()
        selected_game_format = (
            default_game_format
            if default_game_format in available_formats
            else DeckFormatValidator.NO_FORMAT
        )
        self.game_format_combo.set(selected_game_format)

        export_format_label = ctk.CTkLabel(
            form,
            text="Формат файла:",
            anchor="w",
            width=170,
        )
        export_format_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=12,
            pady=10,
        )

        export_labels = DeckSaveService.export_format_labels()
        self.export_format_combo = ctk.CTkComboBox(
            form,
            values=export_labels,
            state="readonly",
        )
        self.export_format_combo.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=12,
            pady=10,
        )
        self.export_format_combo.set(
            default_export_format
            if default_export_format in export_labels
            else export_labels[0]
        )

        self.allow_draft_switch = ctk.CTkSwitch(
            form,
            text=(
                "Разрешить сохранение незавершённой колоды "
                "даже при ошибке количества карт"
            ),
        )
        self.allow_draft_switch.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            padx=12,
            pady=(8, 12),
        )

        validation_header = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        validation_header.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(4, 0),
        )

        validation_title = ctk.CTkLabel(
            validation_header,
            text="Проверка количества карт",
            font=("Arial", 17, "bold"),
            anchor="w",
        )
        validation_title.pack(
            side="left",
            fill="x",
            expand=True,
        )

        validate_button = ctk.CTkButton(
            validation_header,
            text="Проверить",
            command=self.refresh_validation,
            width=120,
        )
        validate_button.pack(side="right")

        self.validation_textbox = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Arial", 13),
        )
        self.validation_textbox.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=20,
            pady=10,
        )
        bind_text_shortcuts(self.validation_textbox)
        self.validation_textbox.configure(state="disabled")

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            justify="left",
            wraplength=700,
        )
        self.status_label.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 8),
        )

        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        buttons.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=20,
            pady=(5, 20),
        )

        internal_button = ctk.CTkButton(
            buttons,
            text="Сохранить в программе",
            command=self._save_internal,
            width=190,
        )
        internal_button.pack(
            side="left",
            padx=(0, 8),
        )

        save_as_button = ctk.CTkButton(
            buttons,
            text="Сохранить как...",
            command=self._save_as,
            width=160,
        )
        save_as_button.pack(
            side="left",
            padx=8,
        )

        close_button = ctk.CTkButton(
            buttons,
            text="Закрыть",
            command=self.destroy,
            width=120,
        )
        close_button.pack(
            side="right",
            padx=(8, 0),
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.destroy,
        )

        self.after(50, self.refresh_validation)
        self.after(100, self.name_entry.focus_set)

    def refresh_validation(self):
        result = DeckFormatValidator.validate(
            deck=self.deck,
            format_name=self.game_format_combo.get(),
        )

        self.validation_textbox.configure(state="normal")
        self.validation_textbox.delete("1.0", "end")
        self.validation_textbox.insert("1.0", result.to_text())
        self.validation_textbox.configure(state="disabled")

        if result.is_valid:
            self.status_label.configure(
                text="Проверка пройдена. Колоду можно сохранить.",
            )
        else:
            self.status_label.configure(
                text=(
                    "Количество карт не соответствует формату. "
                    "Исправьте колоду или включите сохранение черновика."
                ),
            )

        return result

    def _collect_values(self):
        deck_name = self.name_entry.get().strip()

        if not deck_name:
            self.status_label.configure(
                text="Укажите наименование колоды.",
            )
            return None

        result = self.refresh_validation()
        allow_invalid = bool(
            self.allow_draft_switch.get()
        )

        if not result.is_valid and not allow_invalid:
            self.status_label.configure(
                text=(
                    "Сохранение остановлено: количество карт не соответствует "
                    "формату. Исправьте колоду или включите сохранение "
                    "незавершённого черновика."
                ),
            )
            return None

        return {
            "deck_name": deck_name,
            "game_format": self.game_format_combo.get(),
            "export_format": self.export_format_combo.get(),
            "allow_invalid": (
                allow_invalid
                and not result.is_valid
            ),
        }

    def _save_internal(self):
        self._execute_callback(
            self.on_save_internal,
            "Сохранение в библиотеку программы...",
        )

    def _save_as(self):
        self._execute_callback(
            self.on_save_as,
            "Выбор места сохранения...",
        )

    def _execute_callback(self, callback, progress_text):
        values = self._collect_values()

        if values is None:
            return

        if callback is None:
            self.status_label.configure(
                text="Обработчик сохранения не подключён.",
            )
            return

        self.status_label.configure(text=progress_text)
        self.update_idletasks()

        try:
            path = callback(**values)
        except Exception as error:
            self.status_label.configure(
                text=f"Ошибка сохранения: {error}",
            )
            return

        if path is None:
            self.status_label.configure(
                text="Сохранение отменено.",
            )
            return

        self.status_label.configure(
            text=f"Колода сохранена: {path}",
        )
