from providers.mtgdecks_provider import MTGDecksProvider

HTML = """
<html>
    <body>
        <table>
            <tr>
                <th>Archetype</th>
                <th>Meta</th>
            </tr>
            <tr>
                <td>Golgari Midrange</td>
                <td>14%</td>
            </tr>
            <tr>
                <td>Red Deck Wins</td>
                <td>10%</td>
            </tr>
            <tr>
                <td>Selesnya Company</td>
                <td>8%</td>
            </tr>
        </table>
    </body>
</html>
"""


provider = MTGDecksProvider()

print("=" * 60)
print("MTGDECKS PROVIDER TEST")
print("=" * 60)

print()
print("URL CHECKS")
print("Format URL   :", provider.build_format_url("Pioneer"))
print("Decklists URL:", provider.build_decklists_url("Pioneer"))
print("Winrates URL :", provider.build_winrates_url("Pioneer"))

snapshot = provider.parse_meta_html(
    html=HTML,
    format_name="Pioneer",
)

print()
print("SNAPSHOT")
print("Format:", snapshot.format_name)
print("Source:", snapshot.source_name)
print("Count :", snapshot.count)

if snapshot.count != 3:
    raise RuntimeError(f"Ожидалось 3 архетипа, получено {snapshot.count}")

top = snapshot.top_archetypes()

if top[0].name != "Golgari Midrange":
    raise RuntimeError(f"Ожидался Golgari Midrange, получен {top[0].name}")

if top[0].meta_share != 14.0:
    raise RuntimeError(f"Ожидалось 14.0%, получено {top[0].meta_share}")

print()
print("TOP ARCHETYPES")

for archetype in top:
    print(f"{archetype.name} | " f"{archetype.meta_share}%")

print()
print("RESULT: OK")
