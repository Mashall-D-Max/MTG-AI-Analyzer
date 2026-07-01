def bind_text_shortcuts(widget):
    """
    Включает горячие клавиши для CTkEntry и CTkTextbox.

    Работает на русской и английской раскладке Windows.
    """

    widget.bind(
        "<Control-KeyPress>",
        lambda event: _handle_control_key(widget, event),
    )


def _handle_control_key(widget, event):
    action = _get_action(event)

    if action == "select_all":
        return _select_all(widget)

    if action == "copy":
        return _copy(widget)

    if action == "paste":
        return _paste(widget)

    if action == "cut":
        return _cut(widget)

    if action == "undo":
        return _undo(widget)

    if action == "redo":
        return _redo(widget)

    return None


def _get_action(event):
    """
    Определяем действие по keycode и keysym.

    keycode работает по физической клавише.
    keysym нужен как дополнительный fallback.
    """

    keycode = event.keycode

    keysym = str(event.keysym).lower()

    if keycode == 65 or keysym in ("a", "ф"):
        return "select_all"

    if keycode == 67 or keysym in ("c", "с"):
        return "copy"

    if keycode == 86 or keysym in ("v", "м"):
        return "paste"

    if keycode == 88 or keysym in ("x", "ч"):
        return "cut"

    if keycode == 90 or keysym in ("z", "я"):
        return "undo"

    if keycode == 89 or keysym in ("y", "н"):
        return "redo"

    return None


def _is_textbox(widget):
    return hasattr(widget, "tag_add")


def _select_all(widget):
    try:
        if _is_textbox(widget):
            widget.tag_add("sel", "1.0", "end-1c")
            widget.mark_set("insert", "end-1c")
            widget.see("insert")
        else:
            widget.select_range(0, "end")
            widget.icursor("end")

    except Exception:
        pass

    return "break"


def _copy(widget):
    try:
        selected_text = widget.selection_get()

        widget.clipboard_clear()
        widget.clipboard_append(selected_text)

    except Exception:
        pass

    return "break"


def _paste(widget):
    try:
        text = widget.clipboard_get()

        _delete_selection(widget)

        if _is_textbox(widget):
            widget.insert("insert", text)
        else:
            widget.insert(widget.index("insert"), text)

    except Exception:
        pass

    return "break"


def _cut(widget):
    try:
        selected_text = widget.selection_get()

        widget.clipboard_clear()
        widget.clipboard_append(selected_text)

        _delete_selection(widget)

    except Exception:
        pass

    return "break"


def _undo(widget):
    try:
        widget.event_generate("<<Undo>>")
    except Exception:
        pass

    return "break"


def _redo(widget):
    try:
        widget.event_generate("<<Redo>>")
    except Exception:
        pass

    return "break"


def _delete_selection(widget):
    try:
        if _is_textbox(widget):
            widget.delete("sel.first", "sel.last")
        else:
            start = widget.index("sel.first")
            end = widget.index("sel.last")

            widget.delete(start, end)

    except Exception:
        pass
