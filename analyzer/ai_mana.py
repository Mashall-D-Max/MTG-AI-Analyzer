class AIManaAnalyzer:

    COLOR_NAMES = {
        "W": "White",
        "U": "Blue",
        "B": "Black",
        "R": "Red",
        "G": "Green",
    }

    def analyze(self, mana_sources, mana_requirements):

        report = []

        for color in ["W", "U", "B", "R", "G"]:

            required = mana_requirements.get(color, 0)

            if required == 0:
                continue

            sources = mana_sources.get(color, 0)

            report.append(
                {
                    "color": color,
                    "name": self.COLOR_NAMES[color],
                    "required": required,
                    "sources": sources,
                    "ok": sources >= required,
                    "difference": sources - required,
                }
            )

        return report
