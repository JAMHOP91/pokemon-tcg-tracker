"""
Regression test for sites/filters.py - run before every commit (see
CLAUDE.md). Prints each result and exits non-zero if any title is
classified wrongly. Add a title here whenever the filter gets one wrong.
"""

import sys

from sites.filters import is_tcg_product

MUST_PASS = [
    "Mega Evolution Sleeved Booster Pack",
    "Hatterene ex Box",
    "Capture the Moment Collection",
    "Chaos Rising Booster Box",
    "Pitch Black Elite Trainer Box",
    "30th Celebration Poster Collection",
    "30th Celebration Binder Collection",
    "Espeon & Umbreon Premium Deck Set",
    "Mega Evolution Booster Pack",
]

MUST_FAIL = [
    "Squishmallow 10 Inch Pikachu Plush",
    "Basic Fighting Energy Pack",
    "Mega Lucario ex League Battle Deck",
    "Deluxe Battle Deck Koraidon",
    "2025 World Championships Deck",
    "Card Sleeves 100 pack",
    "Ultra Pro Deck Box",
    "Ultra Pro Binder 9-Pocket",
    "Pokemon Poster 24x36",
    "Mini Portfolio (October 2026)",
    "Pitch Black Dice & Coin Set",
    "30th Celebration Poster Collection (Japanese)",
    "Pikachu Plushie",
    "Pokemon Livestream Break",
    "Basic Energies Bundle",
    "Deck Crafter's Collection",
]


def main():
    failures = 0
    for expected, titles in ((True, MUST_PASS), (False, MUST_FAIL)):
        for title in titles:
            result = is_tcg_product(title)
            ok = result == expected
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'}  expected {'pass' if expected else 'fail'}, got {'pass' if result else 'fail'}: {title}")
    total = len(MUST_PASS) + len(MUST_FAIL)
    print(f"\n{total - failures}/{total} correct")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
