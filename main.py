"""
Runs every configured site checker, compares results against previously
seen products, notifies on anything new via Telegram, and saves updated state.
Tracks how long each site has been continuously failing and warns based
on elapsed real time (not raw check count).
Also writes status.json (site health snapshot) and release_history.json
(a running feed of finds) for the dashboard.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from notify import notify_new_products, notify_scraper_warning, notify_scraper_recovered, notify_priority_products
from priority import load_priority_keywords, is_priority_product
from sites import jbhifi
from sites import coolshit
from sites import thegametree
from sites import otakumart
from sites import cardmasters
from sites import hobbylords
from sites import tcgnz
from sites import cardtopia
from sites import wpgames
from sites import collectallday
from sites import celebrationbox_monitor
from sites import coolshit_availability_monitor
from sites import tcgcollectornz
from sites import hobbymaster

STATE_FILE = Path(__file__).parent / "seen_products.json"
STATUS_FILE = Path(__file__).parent / "status.json"
HISTORY_FILE = Path(__file__).parent / "release_history.json"
MAX_HISTORY_ENTRIES = 300

SITES = [
    (jbhifi.SITE_NAME, jbhifi),
    (coolshit.SITE_NAME, coolshit),
    (thegametree.SITE_NAME, thegametree),
    (otakumart.SITE_NAME, otakumart),
    (cardmasters.SITE_NAME, cardmasters),
    (hobbylords.SITE_NAME, hobbylords),
    (tcgnz.SITE_NAME, tcgnz),
    (cardtopia.SITE_NAME, cardtopia),
    (wpgames.SITE_NAME, wpgames),
    (collectallday.SITE_NAME, collectallday),
    (celebrationbox_monitor.SITE_NAME, celebrationbox_monitor),
    (coolshit_availability_monitor.SITE_NAME, coolshit_availability_monitor),
    (tcgcollectornz.SITE_NAME, tcgcollectornz),
    (hobbymaster.SITE_NAME, hobbymaster),
]

DEFAULT_FAILURE_THRESHOLD_MINUTES = 90


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig"))
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8-sig"))
        except Exception:
            return []
    return []


def save_history(history: list) -> None:
    HISTORY_FILE.write_text(json.dumps(history[-MAX_HISTORY_ENTRIES:], indent=2))


def save_status(status: dict) -> None:
    STATUS_FILE.write_text(json.dumps(status, indent=2))


def get_site_state(state: dict, site_name: str) -> dict:
    entry = state.get(site_name)
    if entry is None:
        return {"seen_ids": [], "zero_streak": 0, "warned": False, "first_failure_at": None}
    if isinstance(entry, list):
        return {"seen_ids": entry, "zero_streak": 0, "warned": False, "first_failure_at": None}
    entry.setdefault("first_failure_at", None)
    return entry


def main():
    state = load_state()
    priority_keywords = load_priority_keywords()
    history = load_history()
    status = {}
    now = datetime.now(timezone.utc)

    for site_name, site_module in SITES:
        print(f"Checking {site_name}...")
        site_state = get_site_state(state, site_name)
        seen_ids = set(site_state["seen_ids"])
        allow_empty = getattr(site_module, "ALLOW_EMPTY_RESULTS", False)
        threshold_minutes = getattr(site_module, "FAILURE_THRESHOLD_MINUTES", DEFAULT_FAILURE_THRESHOLD_MINUTES)

        try:
            current_products = site_module.get_current_products()
            fetch_failed = False
        except Exception as e:
            print(f"  Failed to check {site_name}: {e}")
            current_products = None
            fetch_failed = True

        if fetch_failed or (not current_products and not allow_empty):
            if site_state["zero_streak"] == 0 or not site_state.get("first_failure_at"):
                site_state["first_failure_at"] = now.isoformat()
            site_state["zero_streak"] += 1

            first_failure_at = datetime.fromisoformat(site_state["first_failure_at"])
            elapsed_minutes = (now - first_failure_at).total_seconds() / 60
            print(f"  No products found (failing for {elapsed_minutes:.0f} min)")

            if elapsed_minutes >= threshold_minutes and not site_state["warned"]:
                notify_scraper_warning(site_name, int(elapsed_minutes))
                site_state["warned"] = True

            status[site_name] = {
                "last_checked": now.isoformat(),
                "healthy": False,
                "failing_minutes": round(elapsed_minutes),
            }
            state[site_name] = site_state
            continue

        if site_state["warned"]:
            notify_scraper_recovered(site_name)
        site_state["zero_streak"] = 0
        site_state["warned"] = False
        site_state["first_failure_at"] = None

        current_products = current_products or []
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

            for p in new_products:
                history.append({
                    "site": site_name,
                    "title": p["title"],
                    "url": p["url"],
                    "price": p.get("price"),
                    "timestamp": now.isoformat(),
                    "priority": p in priority_matches,
                })
        else:
            print("  No new products")

        status[site_name] = {
            "last_checked": now.isoformat(),
            "healthy": True,
            "failing_minutes": 0,
        }
        site_state["seen_ids"] = list(current_ids)
        state[site_name] = site_state

    save_state(state)
    save_history(history)
    save_status({"generated_at": now.isoformat(), "sites": status})


if __name__ == "__main__":
    main()
