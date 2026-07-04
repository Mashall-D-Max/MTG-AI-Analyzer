from gui.app import App
from gui.scryfall_autocomplete import (
    ScryfallAutocomplete,
)


def main():
    app = App()

    app.scryfall_autocomplete = ScryfallAutocomplete(
        entry=(app.search_panel.quick_query_entry),
        client=(app.search_panel.client),
        on_submit=(app.search_panel.search_quick),
        delay_ms=350,
        minimum_length=2,
        maximum_results=10,
    )

    app.mainloop()


if __name__ == "__main__":
    main()
