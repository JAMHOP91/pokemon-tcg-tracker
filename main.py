"""
Runs every configured site checker, compares results against previously
seen products, notifies on anything new via Telegram, and saves updated state.
Tracks consecutive failures per site and warns if a scraper looks broken.
Sends a separate priority alert for products matching priority_keywords.json.
"""

import json
from pathlib import Path

from notify import notify_new_products, notify_scraper_warning, notify_scraper_recovered, notify_priority_products
from priority import load_priority_keywords, is_priority_product
from sites import jbhifi
from sites import coolshit
from sites import thegametree
from sites import otakumart
from sites import cardmasters
from sites import hobbylords

STATE_FILE = Path(__file__).parent / "seen_products.json"

SITES = [
    (jbhifi.SITE_NAME, jbhifi),
    (coolshit.SITE_NAME, coolshit),
    (thegametree.SITE_NAME, thegametree),
    (otakumart.SITE_NAME, otakumart),
    (cardmasters.SITE_NAME, cardmasters),
    (hobbylords.SITE_NAME, hobbylords),
]

ZERO_STREAK_WARNING_THRESHOLD = 3


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig"))
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_site_state(state: dict, site_name: str) -> dict:
    entry = state.get(site_name)
    if entry is None:
        return {"seen_ids": [], "zero_streak": 0, "warned": False}
    if isinstance(entry, list):
        return {"seen_ids": entry, "zero_streak": 0, "warned": False}
    return entry


def main():
    state = load_state()
    priority_keywords = load_priority_keywords()

    for site_name, site_module in SITES:
        print(f"Checking {site_name}...")
        site_state = get_site_state(state, site_name)
        seen_ids = set(site_state["seen_ids"])

        try:
            current_products = site_module.get_current_products()
        except Exception as e:
            print(f"  Failed to check {site_name}: {e}")
            current_products = None

        if not current_products:
            site_state["zero_streak"] += 1
            print(f"  No products found (zero streak: {site_state['zero_streak']})")
            if site_state["zero_streak"] >= ZERO_STREAK_WARNING_THRESHOLD and not site_state["warned"]:
                notify_scraper_warning(site_name, site_state["zero_streak"])
                site_state["warned"] = True
            state[site_name] = site_state
            continue

        if site_state["warned"]:
            notify_scraper_recovered(site_name)
        site_state["zero_streak"] = 0
        site_state["warned"] = False

        current_ids = {p["id"] for p in current_products}
        new_products = [p for p in current_products if p["id"] not in seen_ids]

        if new_products:
            priority_matches = [p for p in new_products if is_priority_product(p["title"], priority_keywords)]
            regular_matches = [p for p in new_products if p not in priority_matches]

            print(f"  Found {len(new_products)} new product(s)")
            if priority_matches:
                print(f"    {len(priority_matches)} matched priority keywords!")
                notify_priority_products(site_name, priority_matches)
            if regular_matches:
                notify_new_products(site_name, regular_matches)
        else:
            print("  No new products")

        site_state["seen_ids"] = list(current_ids)
        state[site_name] = site_state

    save_state(state)


if __name__ == "__main__":
    main()
