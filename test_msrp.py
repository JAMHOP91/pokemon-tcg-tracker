"""
Regression test for msrp.py - run before every commit (see CLAUDE.md).
No network: requests.get inside msrp is replaced with a stub, and the
exchange rate is injected into the cache. Prints each result and exits
non-zero if anything is wrong.
"""

import sys
import time

import msrp

EXPECTED_KEYS = [
    ("Delta Reign Pokemon Center Elite Trainer Box", ("delta reign", "pokemon center elite trainer box")),
    ("Pokémon Center ETB Delta Reign", ("delta reign", "pokemon center elite trainer box")),
    ("Delta Reign Elite Trainer Box", ("delta reign", "elite trainer box")),
    ("Pokemon TCG Delta Reign ETB", ("delta reign", "elite trainer box")),
    ("Pokemon TCG Mega Evolution Delta Reign Booster Bundle", ("delta reign", "booster bundle")),
    ("Buy Pokemon Mega Evolution Delta Reign Booster Box", ("delta reign", "booster display box")),
    ("Delta Reign Booster Display (36 Packs)", ("delta reign", "booster display box")),
    ("Pokemon Mega Evolution Delta Reign Booster Pack Pre Order", ("delta reign", "booster pack")),
    ("Delta Reign Sleeved Booster Pack", ("delta reign", "booster pack")),
    ("Pokemon TCG Delta Reign Build & Battle Box", ("delta reign", "build and battle box")),
    ("Delta Reign Build and Battle Box", ("delta reign", "build and battle box")),
    ("Pokemon TCG 30th Celebration Elite Trainer Box", ("30th celebration", "elite trainer box")),
    ("30th Celebration Booster Bundle", ("30th celebration", "booster bundle")),
    ("Pokemon TCG: 30th Celebration Espeon ex Box", ("30th celebration", "ex box")),
]

MUST_BE_NONE = [
    # Multi-unit listings
    "Delta Reign Booster Box Case",
    "Delta Reign Elite Trainer Box (Set of 2)",
    "Delta Reign Booster Bundle x3",
    "Delta Reign Booster Display Box 18 Pack",
    "Delta Reign Booster Display Box 18-Pack",
    # Unknown set
    "Surging Sparks Elite Trainer Box",
    "Pokemon TCG Mega Evolution Pitch Black Booster Box",
    # Known set, but no MSRP for that type in that set
    "30th Celebration Pokemon Center Elite Trainer Box",
    "Pokemon: 30th Celebration Booster Pack TCG",
    "Delta Reign Mega Lucario ex Box",
    # No type at all
    "Pokémon TCG: Mega Zygarde EX Premium Collection",
    "Delta Reign Tin - Mega Gardevoir",
    "Pokemon TCG Enhanced 2-Pack Blister – Oddish, Gloom & Vileplume",
    "Pokémon Keldeo 019/086 Rare Holo – Chaos Rising NM",
    "",
]

PRICES = [("$130.00", 130.0), ("NZ$1,299.95", 1299.95), (89.5, 89.5), (None, None), ("", None), ("Sold out", None)]


class _FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"rates": {"NZD": 1.75}}


class _CountingGet:
    """Stands in for requests.get: counts calls, and either returns a
    fixed rate or raises to simulate the API being down."""

    def __init__(self, fail=False):
        self.calls = 0
        self.fail = fail

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if self.fail:
            raise RuntimeError("network disabled in test")
        return _FakeResponse()


def _reset_fx(rate=None):
    msrp._fx_cache.update(rate=rate, fetched_at=time.time() if rate else 0.0, failed_at=0.0)


def main():
    msrp.requests.get = _CountingGet(fail=True)
    failures = 0
    total = 0

    def check(ok, label):
        nonlocal failures, total
        total += 1
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'}  {label}")

    for title, expected in EXPECTED_KEYS:
        got = msrp.product_key(title)
        check(got == expected, f"key {got!r} (expected {expected!r}): {title}")
    for title in MUST_BE_NONE:
        got = msrp.product_key(title)
        check(got is None, f"key {got!r} (expected None): {title}")
    for raw, expected in PRICES:
        got = msrp.parse_price(raw)
        check(got == expected, f"price {raw!r} -> {got!r} (expected {expected!r})")

    # Ratio with an injected rate: ETB 49.99 USD * 1.75 * 1.15 GST = 100.60 NZD
    _reset_fx(1.75)
    got = msrp.msrp_ratio("Delta Reign Elite Trainer Box", "$130.00")
    check(got == 1.29, f"ratio {got!r} (expected 1.29) for $130 Delta Reign ETB at 1.75")
    got = msrp.msrp_ratio("Surging Sparks Elite Trainer Box", "$130.00")
    check(got is None, f"ratio {got!r} (expected None) for unknown set")
    got = msrp.msrp_ratio("Delta Reign Elite Trainer Box", None)
    check(got is None, f"ratio {got!r} (expected None) for missing price")

    # Lazy fetch: a run with only unmatched titles makes zero HTTP calls,
    # and the first matching title fetches once, then the cache is used
    _reset_fx()
    msrp.requests.get = counting = _CountingGet()
    for title in MUST_BE_NONE:
        msrp.msrp_ratio(title, "$130.00")
    check(counting.calls == 0, f"unmatched titles made {counting.calls} HTTP call(s) (expected 0)")
    msrp.msrp_ratio("Delta Reign Elite Trainer Box", "$130.00")
    msrp.msrp_ratio("Delta Reign Booster Bundle", "$60.00")
    check(counting.calls == 1, f"two matching titles made {counting.calls} HTTP call(s) (expected 1)")

    # FX call failing: no crash, no note, and no retry straight away
    _reset_fx()
    msrp.requests.get = failing = _CountingGet(fail=True)
    try:
        ratio = msrp.msrp_ratio("Delta Reign Elite Trainer Box", "$130.00")
        check(ratio is None, f"FX failure gives ratio {ratio!r} (expected None)")
        msrp.msrp_ratio("Delta Reign Booster Bundle", "$60.00")
        check(failing.calls == 1, f"FX failure retried: {failing.calls} call(s) (expected 1)")
    except Exception as e:
        check(False, f"FX failure raised {type(e).__name__}: {e}")

    print(f"\n{total - failures}/{total} correct")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
