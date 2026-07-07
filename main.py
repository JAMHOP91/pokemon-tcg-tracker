"""
Runs every configured site checker, compares results against previously
seen products, notifies on anything new via Telegram, and saves updated state.
"""

import json
import os
from pathlib import Path

from notify import notify_new_products
from sites import jbhifi
from sites import thegametree
from sites import otakumart
from sites import coolshit

STATE_FILE = Path(__file__).parent / "seen_products.json"

# Register each site here: (display name, module with get_current_products())
SITES = [
    (jbhifi.SITE_NAME, jbhifi),
    (coolshit.SITE_NAME, coolshit),
    (thegametree.SITE_NAME, thegametree),
    (otakumart.SITE_NAME, otakumart),
]


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def main():
    state = load_state()

    for site_name, site_module in SITES:
        print(f"Checking {site_name}...")
        try:
            current_products = site_module.get_current_products()
        except Exception as e:
            print(f"  Failed to check {site_name}: {e}")
            continue

        seen_ids = set(state.get(site_name, []))
        current_ids = {p["id"] for p in current_products}

        new_products = [p for p in current_products if p["id"] not in seen_ids]

        if new_products:
            print(f"  Found {len(new_products)} new product(s)")
            notify_new_products(site_name, new_products)
        else:
            print("  No new products")

        # Update state with everything currently seen
        state[site_name] = list(current_ids)

    save_state(state)


if __name__ == "__main__":
    main()
