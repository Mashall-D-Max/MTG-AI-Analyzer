import subprocess
import sys
from pathlib import Path

TESTS = [
    "test_compare_advisor.py",
    "test_meta_compare_basic.py",
    "test_meta_compare_zones.py",
    "test_mana_impact_advisor.py",
    "test_deck_upgrade_builder.py",
    "test_decklist_garbage_filter.py",
    "test_mtgdecks_deck_parser.py",
    "test_mtgdecks_importer.py",
    "tests/smoke_test.py",
]


def run_test(test_file):
    print()
    print("=" * 80)
    print(f"RUNNING: {test_file}")
    print("=" * 80)

    path = Path(test_file)

    if not path.exists():
        print(f"[ERROR] Файл теста не найден: {test_file}")
        return False

    result = subprocess.run(
        [
            sys.executable,
            test_file,
        ],
        text=True,
    )

    if result.returncode != 0:
        print()
        print(f"[FAILED] {test_file}")
        return False

    print()
    print(f"[PASSED] {test_file}")
    return True


def main():
    print("=" * 80)
    print("MTG AI ANALYZER TEST RUNNER")
    print("=" * 80)

    passed = 0
    failed = 0

    for test_file in TESTS:
        ok = run_test(test_file)

        if ok:
            passed += 1
        else:
            failed += 1
            break

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print()
        print("RESULT: FAILED")
        sys.exit(1)

    print()
    print("RESULT: OK")


if __name__ == "__main__":
    main()
