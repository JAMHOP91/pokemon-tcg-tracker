"""
Runs every configured site checker, compares results against previously
seen products, notifies on anything new via Telegram, and saves updated state.
Tracks how long each site has been continuously failing and warns based
on elapsed real time (not raw check count).
Also tracks each product's last-known price and alerts separately if an
already-tracked item's price drops on a later check.
Also writes status.json (site health snapshot) and release_history.json
(a running feed of finds, including a product image where available)
for the dashboard.
"""

import json
import os
import re
import requests
from datetime import datetime, timezone
from pathlib import Path

from notify import notify_new_products, notify_scraper_warning, notify_scraper_recovered, notify_priority_products, notify_price_drops
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
from sites import coolshit_status_watch
from sites import tcgcollectornz
from sites import hobbymaster
from sites import otakumart_preorders
from sites import wpgames_preorders
from sites import gamecorner_preorders
from sites import collectorsguild_preorders
from sites import magicreddragon_preorders
from sites import playx_preorders
from sites import metalife
from sites import tcgcollectornz_preorders
from sites import cardmasters_preorders
from sites import tcgculture
from sites import toytime
from sites import cardtopia_preorders
from sites import mrtofu
from sites import hobbystation
from sites import turtleisland
from sites import ocare
from sites import kidzstuffonline
from sites import parkocards
from sites import hobbyzone
from sites import animalkingdoms
from sites import gamecorner
from sites import cardbot
from sites import popstop
from sites import getthosemons
from sites import sealedandslabbed
from sites import bigpotato

STATE_FILE = Path(__file__).parent / "seen_products.json"
STATUS_FILE = Path(__file__).parent / "status.json"
HISTORY_FILE = Path(__file__).parent / "release_history.json"
MAX_HISTORY_ENTRIES = 1000

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
    (coolshit_status_watch.SITE_NAME, coolshit_status_watch),
    (tcgcollectornz.SITE_NAME, tcgcollectornz),
    (hobbymaster.SITE_NAME, hobbymaster),
    (otakumart_preorders.SITE_NAME, otakumart_preorders),
    (wpgames_preorders.SITE_NAME, wpgames_preorders),
    (gamecorner_preorders.SITE_NAME, gamecorner_preorders),
    (collectorsguild_preorders.SITE_NAME, collectorsguild_preorders),
    (magicreddragon_preorders.SITE_NAME, magicreddragon_preorders),
    (playx_preorders.SITE_NAME, playx_preorders),
    (metalife.SITE_NAME, metalife),
    (tcgcollectornz_preorders.SITE_NAME, tcgcollectornz_preorders),
    (cardmasters_preorders.SITE_NAME, cardmasters_preorders),
    (tcgculture.SITE_NAME, tcgculture),
    (toytime.SITE_NAME, toytime),
    (cardtopia_preorders.SITE_NAME, cardtopia_preorders),
    (mrtofu.SITE_NAME, mrtofu),
    (hobbystation.SITE_NAME, hobbystation),
    (turtleisland.SITE_NAME, turtleisland),
    (ocare.SITE_NAME, ocare),
    (kidzstuffonline.SITE_NAME, kidzstuffonline),
    (parkocards.SITE_NAME, parkocards),
    (hobbyzone.SITE_NAME, hobbyzone),
    (animalkingdoms.SITE_NAME, animalkingdoms),
    (gamecorner.SITE_NAME, gamecorner),
    (cardbot.SITE_NAME, cardbot),
    (popstop.SITE_NAME, popstop),
    (getthosemons.SITE_NAME, getthosemons),
    (sealedandslabbed.SITE_NAME, sealedandslabbed),
    (bigpotato.SITE_NAME, bigpotato),
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
        return {"seen_ids": [], "zero_streak": 0, "warned": False, "first_failure_at": None, "prices": {}}
    if isinstance(entry, list):
        return {"seen_ids": entry, "zero_streak": 0, "warned": False, "first_failure_at": None, "prices": {}}
    entry.setdefault("first_failure_at", None)
    entry.setdefault("prices", {})
    return entry


def parse_price(price_str):
    if not price_str:
        return None
    try:
        cleaned = price_str.replace("$", "").replace(",", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def fetch_og_image(url: str) -> str | None:
    """Fetches a product page's og:image meta tag for the dashboard feed.
    Best-effort only - returns None quickly on any failure."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        match = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            resp.text, re.IGNORECASE,
        )
        if not match:
            match = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                resp.text, re.IGNORECASE,
            )
        return match.group(1) if match else None
    except Exception:
        return None


def ping_heartbeat():
    """Pings Healthchecks.io after a successful run, so it can alert us
    if the pipeline ever stops running entirely. Best-effort only -
    never lets a ping failure break the actual tracker run."""
    url = os.environ.get("HEALTHCHECKS_PING_URL")
    if not url:
        return
    try:
        requests.get(url, timeout=10)
    except Exception:
        pass


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
        prices = site_state.get("prices", {})
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

        price_drops = []
        for p in current_products:
            pid = p["id"]
            new_price = parse_price(p.get("price"))
            old_price = prices.get(pid)
            if pid in seen_ids and new_price is not None and old_price is not None and new_price < old_price:
                price_drops.append({
                    "title": p["title"],
                    "url": p["url"],
                    "old_price": f"${old_price:.2f}",
                    "new_price": f"${new_price:.2f}",
                })
            if new_price is not None:
                prices[pid] = new_price
        site_state["prices"] = prices

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
                    "image": fetch_og_image(p["url"]),
                })
        else:
            print("  No new products")

        if price_drops:
            print(f"  {len(price_drops)} price drop(s)")
            notify_price_drops(site_name, price_drops)

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
    ping_heartbeat()


if __name__ == "__main__":
    main()
