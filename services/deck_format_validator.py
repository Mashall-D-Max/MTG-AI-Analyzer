from dataclasses import dataclass, field


@dataclass(frozen=True)
class DeckFormatRule:
    name: str
    mainboard_minimum: int | None = None
    mainboard_exact: int | None = None
    sideboard_maximum: int | None = None
    sideboard_exact: int | None = None
    note: str = ""


@dataclass(frozen=True)
class DeckValidationIssue:
    level: str
    message: str


@dataclass
class DeckValidationResult:
    format_name: str
    mainboard_size: int
    sideboard_size: int
    rule: DeckFormatRule
    issues: list[DeckValidationIssue] = field(default_factory=list)

    @property
    def errors(self):
        return [
            issue
            for issue in self.issues
            if issue.level == "error"
        ]

    @property
    def warnings(self):
        return [
            issue
            for issue in self.issues
            if issue.level == "warning"
        ]

    @property
    def is_valid(self):
        return not self.errors

    def to_text(self):
        lines = [
            f"Формат: {self.format_name}",
            f"Mainboard: {self.mainboard_size}",
            f"Sideboard: {self.sideboard_size}",
        ]

        if self.rule.note:
            lines.append(f"Правило: {self.rule.note}")

        lines.append("")

        if self.is_valid:
            lines.append("Результат: количество карт соответствует формату.")
        else:
            lines.append("Результат: найдены ошибки количества карт.")

        for issue in self.issues:
            prefix = "Ошибка" if issue.level == "error" else "Предупреждение"
            lines.append(f"{prefix}: {issue.message}")

        lines.append("")
        lines.append(
            "Проверяется только количество карт в Mainboard и Sideboard. "
            "Легальность карт, бан-лист, цветовая идентичность и лимит копий "
            "в этой проверке не анализируются."
        )

        return "\n".join(lines)


class DeckFormatValidator:
    """
    Проверка структуры колоды по количеству карт.

    Правила намеренно ограничены размерами Mainboard и Sideboard.
    Проверка легальности конкретных карт выполняется отдельным этапом.
    """

    NO_FORMAT = "Без формата / без проверки"

    FORMAT_RULES = {
        NO_FORMAT: DeckFormatRule(
            name=NO_FORMAT,
            note="Ограничения количества карт не применяются.",
        ),
        "Standard": DeckFormatRule(
            name="Standard",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Pioneer": DeckFormatRule(
            name="Pioneer",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Explorer": DeckFormatRule(
            name="Explorer",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Modern": DeckFormatRule(
            name="Modern",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Legacy": DeckFormatRule(
            name="Legacy",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Vintage": DeckFormatRule(
            name="Vintage",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Pauper": DeckFormatRule(
            name="Pauper",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Historic": DeckFormatRule(
            name="Historic",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Timeless": DeckFormatRule(
            name="Timeless",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Alchemy": DeckFormatRule(
            name="Alchemy",
            mainboard_minimum=60,
            sideboard_maximum=15,
            note="Минимум 60 карт в Mainboard, Sideboard — не более 15.",
        ),
        "Commander": DeckFormatRule(
            name="Commander",
            mainboard_exact=100,
            sideboard_exact=0,
            note=(
                "Ровно 100 карт, включая командира. "
                "Отдельная зона командира пока не выделяется, поэтому все 100 "
                "карт учитываются в Mainboard."
            ),
        ),
        "Duel Commander": DeckFormatRule(
            name="Duel Commander",
            mainboard_exact=100,
            sideboard_exact=0,
            note=(
                "Ровно 100 карт, включая командира. "
                "Sideboard в текущей модели должен быть пуст."
            ),
        ),
        "Brawl": DeckFormatRule(
            name="Brawl",
            mainboard_exact=60,
            sideboard_exact=0,
            note=(
                "Ровно 60 карт, включая командира. "
                "Sideboard в текущей модели должен быть пуст."
            ),
        ),
        "Standard Brawl": DeckFormatRule(
            name="Standard Brawl",
            mainboard_exact=60,
            sideboard_exact=0,
            note=(
                "Ровно 60 карт, включая командира. "
                "Sideboard в текущей модели должен быть пуст."
            ),
        ),
        "Oathbreaker": DeckFormatRule(
            name="Oathbreaker",
            mainboard_exact=60,
            sideboard_exact=0,
            note=(
                "Ровно 60 карт, включая Oathbreaker и Signature Spell. "
                "Sideboard в текущей модели должен быть пуст."
            ),
        ),
        "Sealed": DeckFormatRule(
            name="Sealed",
            mainboard_minimum=40,
            note=(
                "Минимум 40 карт в Mainboard. "
                "Остальные карты пула могут находиться в Sideboard."
            ),
        ),
        "Booster Draft": DeckFormatRule(
            name="Booster Draft",
            mainboard_minimum=40,
            note=(
                "Минимум 40 карт в Mainboard. "
                "Остальные карты пула могут находиться в Sideboard."
            ),
        ),
    }

    @classmethod
    def available_formats(cls):
        return list(cls.FORMAT_RULES.keys())

    @classmethod
    def validate(cls, deck, format_name):
        if deck is None:
            raise ValueError("Колода не указана")

        normalized_format = str(format_name or cls.NO_FORMAT).strip()

        if normalized_format not in cls.FORMAT_RULES:
            normalized_format = cls.NO_FORMAT

        rule = cls.FORMAT_RULES[normalized_format]

        mainboard_size = int(
            getattr(deck, "mainboard_size", 0)
            or 0
        )

        sideboard_size = int(
            getattr(deck, "sideboard_size", 0)
            or 0
        )

        result = DeckValidationResult(
            format_name=normalized_format,
            mainboard_size=mainboard_size,
            sideboard_size=sideboard_size,
            rule=rule,
        )

        if rule.mainboard_exact is not None:
            if mainboard_size != rule.mainboard_exact:
                difference = rule.mainboard_exact - mainboard_size

                if difference > 0:
                    detail = f"не хватает {difference}"
                else:
                    detail = f"лишних {-difference}"

                result.issues.append(
                    DeckValidationIssue(
                        level="error",
                        message=(
                            f"В Mainboard должно быть ровно "
                            f"{rule.mainboard_exact} карт; сейчас "
                            f"{mainboard_size} ({detail})."
                        ),
                    )
                )

        elif rule.mainboard_minimum is not None:
            if mainboard_size < rule.mainboard_minimum:
                missing = rule.mainboard_minimum - mainboard_size

                result.issues.append(
                    DeckValidationIssue(
                        level="error",
                        message=(
                            f"В Mainboard должно быть минимум "
                            f"{rule.mainboard_minimum} карт; сейчас "
                            f"{mainboard_size}, не хватает {missing}."
                        ),
                    )
                )

        if rule.sideboard_exact is not None:
            if sideboard_size != rule.sideboard_exact:
                result.issues.append(
                    DeckValidationIssue(
                        level="error",
                        message=(
                            f"В Sideboard должно быть ровно "
                            f"{rule.sideboard_exact} карт; сейчас "
                            f"{sideboard_size}."
                        ),
                    )
                )

        elif rule.sideboard_maximum is not None:
            if sideboard_size > rule.sideboard_maximum:
                excess = sideboard_size - rule.sideboard_maximum

                result.issues.append(
                    DeckValidationIssue(
                        level="error",
                        message=(
                            f"В Sideboard разрешено не более "
                            f"{rule.sideboard_maximum} карт; сейчас "
                            f"{sideboard_size}, лишних {excess}."
                        ),
                    )
                )

        if mainboard_size == 0 and normalized_format == cls.NO_FORMAT:
            result.issues.append(
                DeckValidationIssue(
                    level="warning",
                    message="Mainboard пуст.",
                )
            )

        return result
