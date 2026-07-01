from utils.mana_symbols import format_mana_cost

cases = {
    "{1}{W}{B}": "① ⚪ ⚫",
    "{2}{U}": "② 🔵",
    "{X}{R}": "Ⓧ 🔴",
    "{W/B}": "⚪/⚫",
    "{2/W}": "②/⚪",
}


print("=" * 60)
print("MANA SYMBOLS TEST")
print("=" * 60)

for source, expected in cases.items():
    result = format_mana_cost(source)

    print(f"{source} -> {result}")

    if result != expected:
        raise RuntimeError(f"Ошибка: ожидалось {expected}, получено {result}")

print()
print("RESULT: OK")
