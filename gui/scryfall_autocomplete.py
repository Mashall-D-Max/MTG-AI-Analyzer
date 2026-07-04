import threading
import tkinter as tk


class ScryfallAutocomplete:
    """
    Выпадающие подсказки для строки поиска Scryfall.

    Особенности:
    - запрос выполняется с задержкой после ввода;
    - сетевой запрос работает в отдельном потоке;
    - устаревшие результаты игнорируются;
    - подсказку можно выбрать мышью или клавиатурой.
    """

    IGNORED_KEYS = {
        "Up",
        "Down",
        "Left",
        "Right",
        "Return",
        "Escape",
        "Tab",
        "Shift_L",
        "Shift_R",
        "Control_L",
        "Control_R",
        "Alt_L",
        "Alt_R",
        "Home",
        "End",
        "Prior",
        "Next",
    }

    def __init__(
        self,
        entry,
        client,
        on_submit=None,
        delay_ms=350,
        minimum_length=2,
        maximum_results=10,
    ):
        self.entry = entry
        self.client = client
        self.on_submit = on_submit

        self.delay_ms = delay_ms
        self.minimum_length = minimum_length
        self.maximum_results = maximum_results

        self.after_id = None
        self.request_number = 0
        self.current_suggestions = []

        self.popup = None
        self.listbox = None

        self._create_popup()
        self._bind_events()

    # ======================================================
    # Создание окна подсказок
    # ======================================================

    def _create_popup(self):
        root_window = self.entry.winfo_toplevel()

        self.popup = tk.Toplevel(root_window)

        self.popup.withdraw()
        self.popup.overrideredirect(True)

        try:
            self.popup.attributes(
                "-topmost",
                True,
            )
        except tk.TclError:
            pass

        self.listbox = tk.Listbox(
            self.popup,
            bg="#202020",
            fg="#f0f0f0",
            selectbackground="#1f6aa5",
            selectforeground="#ffffff",
            borderwidth=1,
            relief="solid",
            highlightthickness=0,
            activestyle="none",
            font=("Arial", 11),
            exportselection=False,
        )

        self.listbox.pack(
            fill="both",
            expand=True,
        )

    # ======================================================
    # События
    # ======================================================

    def _bind_events(self):
        self.entry.bind(
            "<KeyRelease>",
            self._on_entry_key_release,
            add="+",
        )

        self.entry.bind(
            "<Down>",
            self._focus_first_suggestion,
            add="+",
        )

        self.entry.bind(
            "<Escape>",
            self._hide_popup,
            add="+",
        )

        self.entry.bind(
            "<FocusOut>",
            self._on_entry_focus_out,
            add="+",
        )

        self.entry.bind(
            "<Configure>",
            self._on_entry_configure,
            add="+",
        )

        self.listbox.bind(
            "<ButtonRelease-1>",
            self._on_listbox_click,
        )

        self.listbox.bind(
            "<Double-Button-1>",
            self._on_listbox_double_click,
        )

        self.listbox.bind(
            "<Return>",
            self._on_listbox_return,
        )

        self.listbox.bind(
            "<Escape>",
            self._return_focus_to_entry,
        )

        self.listbox.bind(
            "<Up>",
            self._on_listbox_up,
        )

        self.listbox.bind(
            "<FocusOut>",
            self._on_listbox_focus_out,
        )

        root_window = self.entry.winfo_toplevel()

        root_window.bind(
            "<Configure>",
            self._on_root_configure,
            add="+",
        )

    # ======================================================
    # Ввод текста
    # ======================================================

    def _on_entry_key_release(self, event):
        if event.keysym in self.IGNORED_KEYS:
            return

        query = self.entry.get().strip()

        self.request_number += 1
        current_request = self.request_number

        self._cancel_pending_request()

        if len(query) < self.minimum_length:
            self.current_suggestions = []
            self._hide_popup()
            return

        self.after_id = self.entry.after(
            self.delay_ms,
            lambda: self._start_request(
                query=query,
                request_number=current_request,
            ),
        )

    def _cancel_pending_request(self):
        if self.after_id is None:
            return

        try:
            self.entry.after_cancel(self.after_id)
        except tk.TclError:
            pass

        self.after_id = None

    # ======================================================
    # Загрузка подсказок
    # ======================================================

    def _start_request(
        self,
        query,
        request_number,
    ):
        self.after_id = None

        thread = threading.Thread(
            target=self._request_worker,
            args=(
                query,
                request_number,
            ),
            daemon=True,
        )

        thread.start()

    def _request_worker(
        self,
        query,
        request_number,
    ):
        try:
            suggestions = self.client.autocomplete(query)

            suggestions = suggestions[: self.maximum_results]

            self.entry.after(
                0,
                self._show_request_result,
                query,
                request_number,
                suggestions,
            )

        except Exception:
            self.entry.after(
                0,
                self._show_request_result,
                query,
                request_number,
                [],
            )

    def _show_request_result(
        self,
        query,
        request_number,
        suggestions,
    ):
        if request_number != self.request_number:
            return

        current_query = self.entry.get().strip()

        if current_query != query:
            return

        self.current_suggestions = list(suggestions)

        self.listbox.delete(
            0,
            "end",
        )

        for suggestion in self.current_suggestions:
            self.listbox.insert(
                "end",
                suggestion,
            )

        if not self.current_suggestions:
            self._hide_popup()
            return

        self._position_popup()
        self.popup.deiconify()
        self.popup.lift()

    # ======================================================
    # Позиционирование
    # ======================================================

    def _position_popup(self):
        try:
            self.entry.update_idletasks()

            x = self.entry.winfo_rootx()

            y = self.entry.winfo_rooty() + self.entry.winfo_height()

            width = max(
                self.entry.winfo_width(),
                350,
            )

            visible_rows = min(
                len(self.current_suggestions),
                self.maximum_results,
            )

            height = max(
                32,
                visible_rows * 28,
            )

            self.popup.geometry(f"{width}x{height}+{x}+{y}")

        except tk.TclError:
            self._hide_popup()

    def _on_entry_configure(self, event):
        if self._popup_is_visible():
            self._position_popup()

    def _on_root_configure(self, event):
        if self._popup_is_visible():
            self._position_popup()

    # ======================================================
    # Управление клавиатурой
    # ======================================================

    def _focus_first_suggestion(
        self,
        event=None,
    ):
        if not self._popup_is_visible():
            return

        if not self.current_suggestions:
            return

        self.listbox.focus_set()

        self.listbox.selection_clear(
            0,
            "end",
        )

        self.listbox.selection_set(0)
        self.listbox.activate(0)
        self.listbox.see(0)

        return "break"

    def _on_listbox_up(self, event):
        selection = self.listbox.curselection()

        if not selection:
            self._return_focus_to_entry()
            return "break"

        if selection[0] <= 0:
            self._return_focus_to_entry()
            return "break"

        return None

    def _return_focus_to_entry(
        self,
        event=None,
    ):
        self.entry.focus_set()
        self._hide_popup()

        return "break"

    # ======================================================
    # Выбор подсказки
    # ======================================================

    def _on_listbox_click(self, event):
        self.listbox.focus_set()

    def _on_listbox_double_click(
        self,
        event,
    ):
        self._select_current_suggestion(submit=True)

        return "break"

    def _on_listbox_return(
        self,
        event,
    ):
        self._select_current_suggestion(submit=True)

        return "break"

    def _select_current_suggestion(
        self,
        submit,
    ):
        selection = self.listbox.curselection()

        if not selection:
            return

        index = selection[0]

        if index >= len(self.current_suggestions):
            return

        suggestion = self.current_suggestions[index]

        self.request_number += 1
        self._cancel_pending_request()

        self.entry.delete(
            0,
            "end",
        )

        self.entry.insert(
            0,
            suggestion,
        )

        self.entry.icursor("end")

        self.entry.focus_set()

        self.current_suggestions = []
        self._hide_popup()

        if submit and self.on_submit is not None:
            self.entry.after(
                10,
                self.on_submit,
            )

    # ======================================================
    # Скрытие окна
    # ======================================================

    def _on_entry_focus_out(
        self,
        event,
    ):
        self.entry.after(
            150,
            self._hide_if_focus_outside,
        )

    def _on_listbox_focus_out(
        self,
        event,
    ):
        self.entry.after(
            150,
            self._hide_if_focus_outside,
        )

    def _hide_if_focus_outside(self):
        try:
            focused_widget = self.entry.focus_get()
        except tk.TclError:
            focused_widget = None

        if focused_widget in {
            self.entry,
            self.listbox,
        }:
            return

        self._hide_popup()

    def _hide_popup(
        self,
        event=None,
    ):
        if self.popup is None:
            return

        try:
            self.popup.withdraw()
        except tk.TclError:
            pass

    def _popup_is_visible(self):
        if self.popup is None:
            return False

        try:
            return bool(self.popup.winfo_viewable())
        except tk.TclError:
            return False

    # ======================================================
    # Завершение работы
    # ======================================================

    def destroy(self):
        self.request_number += 1

        self._cancel_pending_request()

        if self.popup is not None:
            try:
                self.popup.destroy()
            except tk.TclError:
                pass

        self.popup = None
        self.listbox = None
