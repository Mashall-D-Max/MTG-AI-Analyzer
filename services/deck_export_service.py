from pathlib import Path


class DeckExportService:
    """
    Сервис сохранения decklist в текстовый файл.
    """

    def save_deck_text(
        self,
        deck_text,
        filename="upgraded_deck.txt",
        folder="decks",
    ):
        if not deck_text:
            raise ValueError("Текст колоды пустой")

        folder_path = Path(folder)

        folder_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = folder_path / filename

        file_path.write_text(
            deck_text,
            encoding="utf-8",
        )

        return file_path
