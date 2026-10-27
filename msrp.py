"""
MSRP comparison for alerts and the dashboard. Matches a known set and a
product type from the title, converts that product's US MSRP to an
expected NZ price (USD -> NZD at today's rate, plus 15% GST) and returns
price / expected as a ratio.

Anything else gets None, so no note is shown: an unknown set, a type
with no MSRP for that set, a multi-unit listing (case, set of 2, x3,
18 pack), a missing price, or no usable exchange rate.
"""

import re
import time

import requests

# (set, product type) -> US MSRP in USD. Add a set to SET_PATTERNS and
# its types here; a type missing for a set means no note for that set.
MSRP_USD = {
    ("delta reign", "elite trainer box"): 49.99,
    ("delta reign", "pokemon center elite trainer box"): 59.99,
    ("delta reign", "booster bundle"): 26.94,
    ("delta reign", "booster display box"): 161.64,
    ("delta reign", "booster pack"): 4.49,
    ("delta reign", "build and battle box"): 21.99,
    ("30th celebration", "elite trainer box"): 49.99,
    ("30th celebration", "booster bundle"): 26.94,
    ("30th celebration", "ex box"): 21.99,
}

SET_PATTERNS = [
    ("delta reign", re.compile(r"\bdelta\s+reign\b")),
    ("30th celebration", re.compile(r"\b30th\s+celebration\b")),
]

# Checked in order, first match wins - so the Pokemon Center ETB is
# checked before the plain ETB (and a 30th Celebration Pokemon Center
# ETB gets no note rather than the plain ETB price), and the
# bundle/display box before the single pack.
TYPE_PATTERNS = [
    ("pokemon center elite trainer box", re.compile(r"\bpokemon\s+center\b.*\b(elite\s+trainer\s+box|etb)\b")),
    ("elite trainer box", re.compile(r"\b(elite\s+trainer\s+box|etb)\b")),
    ("booster bundle", re.compile(r"\bbooster\s+bundle\b")),
    ("booster display box", re.compile(r"\bbooster\s+(display|box)\b")),
    ("booster pack", re.compile(r"\bbooster\s+pack\b")),
    ("build and battle box", re.compile(r"\bbuild\s*(&|and)\s*battle\s+box\b")),
    ("ex box", re.compile(r"\bex\s+box\b")),
]

# Multi-unit listings - the single-unit MSRP would make these look
# several times overpriced, so they get no note
MULTI_UNIT_PATTERN = re.compile(r"\bcase\b|\bset\s+of\b|\bx\d+\b|\b18[\s-]packs?\b")

GST = 1.15
FX_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=NZD"
FX_CACHE_SECONDS = 24 * 60 * 60
# After a failed fetch, wait before retrying so one run with many
# products doesn't stall on a down API once per product
FX_RETRY_SECONDS = 60 * 60

_fx_cache = {"rate": None, "fetched_at": 0.0, "failed_at": 0.0}


def _normalize(text: str) -> str:
    return text.lower().replace("é", "e")


def product_key(title: str) -> tuple[str, str] | None:
    """(set, type) when the title is a single unit of a product with a
    known MSRP, else None."""
    text = _normalize(title or "")
    if MULTI_UNIT_PATTERN.search(text):
        return None
    set_name = next((name for name, pattern in SET_PATTERNS if pattern.search(text)), None)
    if set_name is None:
        return None
    type_name = next((name for name, pattern in TYPE_PATTERNS if pattern.search(text)), None)
    key = (set_name, type_name)
    return key if key in MSRP_USD else None


def usd_to_nzd_rate() -> float | None:
    """Today's USD -> NZD rate, cached in memory for 24h. None if the
    API call fails (the caller then shows no note)."""
    now = time.time()
    if _fx_cache["rate"] is not None and now - _fx_cache["fetched_at"] < FX_CACHE_SECONDS:
        return _fx_cache["rate"]
    if now - _fx_cache["failed_at"] < FX_RETRY_SECONDS:
        return None
    try:
        resp = requests.get(FX_URL, timeout=10)
        resp.raise_for_status()
        rate = float(resp.json()["rates"]["NZD"])
    except Exception as e:
        print(f"  MSRP: exchange rate fetch failed: {e}")
        _fx_cache["failed_at"] = now
        return None
    _fx_cache.update(rate=rate, fetched_at=now, failed_at=0.0)
    return rate


def parse_price(price) -> float | None:
    """'$130.00' / 'NZ$1,299.95' / 130 -> float, or None."""
    if isinstance(price, (int, float)):
        return float(price)
    if not price:
        return None
    match = re.search(r"\d[\d,]*(?:\.\d+)?", str(price))
    return float(match.group().replace(",", "")) if match else None


def msrp_ratio(title: str, price) -> float | None:
    """Price as a multiple of the expected NZ price for this set and
    type, rounded to 2 dp. None when the product, price or rate is
    unknown. The rate is only fetched once a title has matched, so a
    run with no known products makes no HTTP call."""
    key = product_key(title)
    if key is None:
        return None
    nzd_price = parse_price(price)
    if not nzd_price:
        return None
    rate = usd_to_nzd_rate()
    if rate is None:
        return None
    expected_nzd = MSRP_USD[key] * rate * GST
    return round(nzd_price / expected_nzd, 2)
