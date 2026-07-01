import re

MANA_TOKEN_PATTERN = re.compile(r"\{([^}]+)\}")


GENERIC_MANA_SYMBOLS = {
    "0": "⓪",
    "1": "①",
    "2": "②",
    "3": "③",
    "4": "④",
    "5": "⑤",
    "6": "⑥",
    "7": "⑦",
    "8": "⑧",
    "9": "⑨",
    "10": "⑩",
    "11": "⑪",
    "12": "⑫",
    "13": "⑬",
    "14": "⑭",
    "15": "⑮",
    "16": "⑯",
    "17": "⑰",
    "18": "⑱",
    "19": "⑲",
    "20": "⑳",
}


COLOR_MANA_SYMBOLS = {
    "W": "⚪",
    "U": "🔵",
    "B": "⚫",
    "R": "🔴",
    "G": "🟢",
    "C": "◇",
    "X": "Ⓧ",
    "Y": "Ⓨ",
    "Z": "Ⓩ",
    "S": "❄",
    "P": "Φ",
}


def format_mana_cost(mana_cost):
    """
    Преобразует mana cost Scryfall в более красивый вид.

    Пример:
    {1}{W}{B} -> ① ⚪ ⚫
    {2}{U}    -> ② 🔵
    {W/B}     -> ⚪/⚫
    """

    if not mana_cost:
        return ""

    tokens = MANA_TOKEN_PATTERN.findall(mana_cost)

    if not tokens:
        return str(mana_cost)

    return " ".join(format_mana_token(token) for token in tokens)


def format_mana_token(token):
    token = str(token).upper().strip()

    if token in GENERIC_MANA_SYMBOLS:
        return GENERIC_MANA_SYMBOLS[token]

    if token in COLOR_MANA_SYMBOLS:
        return COLOR_MANA_SYMBOLS[token]

    if "/" in token:
        parts = token.split("/")

        return "/".join(format_mana_token(part) for part in parts)

    return token
