from providers.mtgdecks_provider import MTGDecksProvider

HTML = """
<html>
    <body>
        <h2>Decklist</h2>

        <h3>Creature [4]</h3>
        <div>4 Ketramose, the New Dawn $1.00 $0.50 M</div>

        <h3>Instant [4]</h3>
        <div>4 Fatal Push $0.50 $0.20 U</div>

        <h3>Sorcery [4]</h3>
        <div>4 Thoughtseize $10.00 $2.00 R</div>

        <h3>Land [4]</h3>
        <div>2 Plains $0.01 $0.01 C</div>
        <div>2 Swamp $0.01 $0.01 C</div>

        <h3>Sideboard [2]</h3>
        <div>2 Duress $0.10 $0.01 C</div>

        <h2>Buy this deck:</h2>
    </body>
</html>
"""


provider = MTGDecksProvider()

print("=" * 60)
print("MTGDECKS DECK PARSER TEST")
print("=" * 60)

deck_text = provider.extract_deck_text(HTML)

print()
print("EXTRACTED DECK TEXT")
print(deck_text)

if "Deck" not in deck_text:
    raise RuntimeError("В извлечённом тексте нет Deck")

if "Sideboard" not in deck_text:
    raise RuntimeError("В извлечённом тексте нет Sideboard")

if "4 Fatal Push" not in deck_text:
    raise RuntimeError("Fatal Push не найден")

deck = provider.parse_deck_html(HTML)

print()
print("DECK")
print("Mainboard:", deck.mainboard_size)
print("Sideboard:", deck.sideboard_size)
print("Total:", deck.total_size)

if deck.mainboard_size != 16:
    raise RuntimeError(f"Ожидалось 16 карт mainboard, получено {deck.mainboard_size}")

if deck.sideboard_size != 2:
    raise RuntimeError(f"Ожидалось 2 карты sideboard, получено {deck.sideboard_size}")

if deck.total_size != 18:
    raise RuntimeError(f"Ожидалось 18 карт всего, получено {deck.total_size}")

print()
print("RESULT: OK")
