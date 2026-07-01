from meta.archetype import Archetype
from meta.meta_snapshot import MetaSnapshot

snapshot = MetaSnapshot(
    format_name="Pioneer",
    source_name="Test",
)

snapshot.add_archetype(
    Archetype(
        name="Orzhov Ketramose",
        format_name="Pioneer",
        colors=["W", "B"],
        tier="Tier 1",
        meta_share=10.5,
        win_rate=55.2,
    )
)

snapshot.add_archetype(
    Archetype(
        name="Izzet Phoenix",
        format_name="Pioneer",
        colors=["U", "R"],
        tier="Tier 1",
        meta_share=8.3,
        win_rate=53.7,
    )
)

print("=" * 60)
print("META SNAPSHOT TEST")
print("=" * 60)

print(f"Format : {snapshot.format_name}")
print(f"Source : {snapshot.source_name}")
print(f"Count  : {snapshot.count}")

print()
print("TOP ARCHETYPES")

for archetype in snapshot.top_archetypes():
    print(
        f"{archetype.name} | "
        f"{archetype.meta_share}% | "
        f"{archetype.win_rate}% | "
        f"{archetype.tier}"
    )

found = snapshot.find_archetype("Orzhov Ketramose")

if found is None:
    raise RuntimeError("Архетип Orzhov Ketramose не найден")

print()
print("RESULT: OK")
