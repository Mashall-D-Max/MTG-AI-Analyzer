import re


class ScryfallQueryBuilder:
    """
    Создаёт поисковую строку для Scryfall на основании
    значений формы расширенного поиска.
    """

    VALID_OPERATORS = {
        "=",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
    }

    COLOR_ORDER = (
        "W",
        "U",
        "B",
        "R",
        "G",
        "C",
    )

    STAT_FIELDS = {
        "mana_value": "mv",
        "power": "power",
        "toughness": "toughness",
        "loyalty": "loyalty",
    }

    @classmethod
    def build(cls, filters):
        if filters is None:
            filters = {}

        terms = []

        cls._append_raw_query(
            terms,
            filters.get("raw_query"),
        )

        cls._append_text_term(
            terms,
            "name",
            filters.get("name"),
        )

        cls._append_text_term(
            terms,
            "oracle",
            filters.get("oracle"),
        )

        cls._append_text_term(
            terms,
            "type",
            filters.get("type_line"),
        )

        cls._append_or_group(
            terms,
            prefix="type",
            values=filters.get("types"),
        )

        cls._append_color_term(
            terms,
            prefix="color",
            colors=filters.get("colors"),
            comparison=filters.get(
                "color_comparison",
                "=",
            ),
        )

        cls._append_color_term(
            terms,
            prefix="id",
            colors=filters.get("identity"),
            comparison=filters.get(
                "identity_comparison",
                "<=",
            ),
        )

        cls._append_text_term(
            terms,
            "mana",
            filters.get("mana_cost"),
        )

        for filter_name, scryfall_name in cls.STAT_FIELDS.items():
            cls._append_numeric_term(
                terms=terms,
                prefix=scryfall_name,
                operator=filters.get(
                    f"{filter_name}_operator",
                    "=",
                ),
                value=filters.get(filter_name),
            )

        cls._append_or_group(
            terms,
            prefix="game",
            values=filters.get("games"),
        )

        cls._append_legality_term(
            terms,
            status=filters.get("format_status"),
            format_name=filters.get("format"),
        )

        cls._append_or_group(
            terms,
            prefix="set",
            values=filters.get("sets"),
        )

        cls._append_or_group(
            terms,
            prefix="block",
            values=filters.get("blocks"),
        )

        cls._append_or_group(
            terms,
            prefix="rarity",
            values=filters.get("rarities"),
        )

        cls._append_criteria(
            terms,
            filters.get("criteria"),
        )

        cls._append_price_term(
            terms,
            currency=filters.get("price_currency"),
            operator=filters.get("price_operator"),
            value=filters.get("price_value"),
        )

        cls._append_text_term(
            terms,
            "artist",
            filters.get("artist"),
        )

        cls._append_text_term(
            terms,
            "flavor",
            filters.get("flavor"),
        )

        cls._append_text_term(
            terms,
            "lore",
            filters.get("lore"),
        )

        cls._append_language_term(
            terms,
            filters.get("language"),
        )

        return " ".join(term for term in terms if term).strip()

    # ======================================================
    # Raw query
    # ======================================================

    @staticmethod
    def _append_raw_query(terms, value):
        value = ScryfallQueryBuilder._clean(value)

        if value:
            terms.append(value)

    # ======================================================
    # Text values
    # ======================================================

    @classmethod
    def _append_text_term(
        cls,
        terms,
        prefix,
        value,
    ):
        value = cls._clean(value)

        if not value:
            return

        terms.append(f"{prefix}:{cls._quote(value)}")

    # ======================================================
    # Multiple values
    # ======================================================

    @classmethod
    def _append_or_group(
        cls,
        terms,
        prefix,
        values,
    ):
        normalized_values = cls._normalize_values(values)

        if not normalized_values:
            return

        expressions = [
            f"{prefix}:{cls._quote_if_needed(value)}" for value in normalized_values
        ]

        if len(expressions) == 1:
            terms.append(expressions[0])
            return

        terms.append("(" + " OR ".join(expressions) + ")")

    # ======================================================
    # Colors
    # ======================================================

    @classmethod
    def _append_color_term(
        cls,
        terms,
        prefix,
        colors,
        comparison,
    ):
        normalized_colors = cls._normalize_colors(colors)

        if not normalized_colors:
            return

        if comparison not in {
            "=",
            ">=",
            "<=",
        }:
            comparison = "="

        color_value = "".join(normalized_colors)

        terms.append(f"{prefix}{comparison}{color_value}")

    @classmethod
    def _normalize_colors(cls, colors):
        values = cls._normalize_values(colors)

        normalized = []

        for color in cls.COLOR_ORDER:
            if color in {value.upper() for value in values}:
                normalized.append(color)

        # Цветная карта не может одновременно считаться
        # бесцветной в обычном сравнении цветов.
        if "C" in normalized and len(normalized) > 1:
            normalized.remove("C")

        return normalized

    # ======================================================
    # Numeric values
    # ======================================================

    @classmethod
    def _append_numeric_term(
        cls,
        terms,
        prefix,
        operator,
        value,
    ):
        value = cls._clean(value)

        if value == "":
            return

        operator = cls._normalize_operator(
            operator,
            default="=",
        )

        terms.append(f"{prefix}{operator}{value}")

    # ======================================================
    # Legality
    # ======================================================

    @classmethod
    def _append_legality_term(
        cls,
        terms,
        status,
        format_name,
    ):
        status = cls._clean(status).lower()
        format_name = cls._clean(format_name).lower()

        if not format_name:
            return

        if status not in {
            "legal",
            "banned",
            "restricted",
        }:
            status = "legal"

        terms.append(f"{status}:{cls._quote_if_needed(format_name)}")

    # ======================================================
    # Criteria
    # ======================================================

    @classmethod
    def _append_criteria(
        cls,
        terms,
        values,
    ):
        normalized_values = cls._normalize_values(values)

        for value in normalized_values:
            terms.append(f"is:{cls._quote_if_needed(value)}")

    # ======================================================
    # Price
    # ======================================================

    @classmethod
    def _append_price_term(
        cls,
        terms,
        currency,
        operator,
        value,
    ):
        currency = cls._clean(currency).lower()
        value = cls._clean(value)

        if not currency or value == "":
            return

        if currency not in {
            "usd",
            "eur",
            "tix",
        }:
            return

        operator = cls._normalize_operator(
            operator,
            default="<=",
        )

        terms.append(f"{currency}{operator}{value}")

    # ======================================================
    # Language
    # ======================================================

    @classmethod
    def _append_language_term(
        cls,
        terms,
        language,
    ):
        language = cls._clean(language).lower()

        if language in {
            "",
            "default",
            "any",
        }:
            return

        terms.append(f"lang:{cls._quote_if_needed(language)}")

    # ======================================================
    # Helpers
    # ======================================================

    @classmethod
    def _normalize_operator(
        cls,
        operator,
        default,
    ):
        operator = cls._clean(operator)

        if operator not in cls.VALID_OPERATORS:
            return default

        return operator

    @classmethod
    def _normalize_values(cls, values):
        if values is None:
            return []

        if isinstance(values, str):
            values = [values]

        result = []

        for value in values:
            clean_value = cls._clean(value)

            if clean_value and clean_value not in result:
                result.append(clean_value)

        return result

    @staticmethod
    def _clean(value):
        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _quote(value):
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')

        return f'"{escaped}"'

    @classmethod
    def _quote_if_needed(cls, value):
        value = cls._clean(value)

        if re.fullmatch(
            r"[A-Za-z0-9_-]+",
            value,
        ):
            return value

        return cls._quote(value)
