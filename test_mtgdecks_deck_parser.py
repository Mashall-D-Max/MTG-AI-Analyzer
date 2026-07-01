from providers.mtgdecks_provider import MTGDecksProvider

HTML = """
<html>
    <body>
        <h2>Decklist</h2>

        <h3>Maindeck (60)</h3>

        <h3>Creature [4]</h3>
        <div>4</div>
        <div>Ketramose, the New Dawn</div>
        <div>$1.00</div>
        <div>$0.50</div>
        <div>M</div>

        <h3>Instant [4]</h3>
        <div>4</div>
        <div>Fatal Push</div>
        <div>$0.50</div>
        <div>$0.20</div>
        <div>U</div>

        <h3>Sorcery [4]</h3>
        <div>4</div>
        <div>Thoughtseize</div>
        <div>$10.00</div>
        <div>$2.00</div>
        <div>R</div>

        <h3>Land [4]</h3>
        <div>2</div>
        <div>Plains</div>
        <div>$0.01</div>
        <div>$0.01</div>
        <div>C</div>

        <div>2</div>
        <div>Swamp</div>
        <div>$0.01</div>
        <div>$0.01</div>
        <div>C</div>

        <h3>Sideboard [2]</h3>
        <div>2</div>
        <div>Duress</div>
        <div>$0.10</div>
        <div>$0.01</div>
        <div>C</div>

        <h2>Buy this deck:</h2>
    </body>
</html>
"""


EXPORT_HTML = """
<html>
    <body>
        <div>
            Copy to clipboard and import!
            Deck
            4 Fatal Push
            4 Thoughtseize
            4 Ketramose, the New Dawn
            2 Plains
            2 Swamp
            Sideboard
            2 Duress
        </div>
    </body>
</html>
"""


provider = MTGDecksProvider()

print("=" * 60)
print("MTGDECKS DECK PARSER TEST")
print("=" * 60)

deck_text = provider.extract_deck_text(HTML)

print()
print("EXTRACTED STRUCTURED DECK TEXT")
print(deck_text)

if "Deck" not in deck_text:
    raise RuntimeError("В извлечённом тексте нет Deck")

if "Sideboard" not in deck_text:
    raise RuntimeError("В извлечённом тексте нет Sideboard")

if "4 Fatal Push" not in deck_text:
    raise RuntimeError("Fatal Push не найден")

deck = provider.parse_deck_html(HTML)

print()
print("STRUCTURED DECK")
print("Mainboard:", deck.mainboard_size)
print("Sideboard:", deck.sideboard_size)
print("Total:", deck.total_size)

if deck.mainboard_size != 16:
    raise RuntimeError(f"Ожидалось 16 карт mainboard, получено {deck.mainboard_size}")

if deck.sideboard_size != 2:
    raise RuntimeError(f"Ожидалось 2 карты sideboard, получено {deck.sideboard_size}")

if deck.total_size != 18:
    raise RuntimeError(f"Ожидалось 18 карт всего, получено {deck.total_size}")

export_deck_text = provider.extract_deck_text(EXPORT_HTML)

print()
print("EXTRACTED EXPORT DECK TEXT")
print(export_deck_text)

if "4 Thoughtseize" not in export_deck_text:
    raise RuntimeError("Thoughtseize не найден в export deck text")

export_deck = provider.parse_deck_html(EXPORT_HTML)

print()
print("EXPORT DECK")
print("Mainboard:", export_deck.mainboard_size)
print("Sideboard:", export_deck.sideboard_size)
print("Total:", export_deck.total_size)

if export_deck.mainboard_size != 16:
    raise RuntimeError(
        f"Ожидалось 16 карт mainboard, получено {export_deck.mainboard_size}"
    )

if export_deck.sideboard_size != 2:
    raise RuntimeError(
        f"Ожидалось 2 карты sideboard, получено {export_deck.sideboard_size}"
    )

if export_deck.total_size != 18:
    raise RuntimeError(f"Ожидалось 18 карт всего, получено {export_deck.total_size}")

print()
print("RESULT: OK")
