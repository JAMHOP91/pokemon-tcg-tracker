"""
Cool Shit - Watchlist.

Tracks a small LIST of specific product slugs (not the whole site),
alerting when any of their status changes (e.g. "Coming soon" flips
to available/sold out). Add a new slug to WATCHED_SLUGS whenever
there's a specific known upcoming item worth tracking closely - the
slug is the last part of the product URL, e.g. for
"coolshit.co.nz/product/deltaetb" the slug is "deltaetb".
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from sites.retry_helper import with_retries

SITE_NAME = "Cool Shit - Watchlist"
LISTING_URL = "https://www.coolshit.co.nz/category/pokemon"
PRODUCT_CARD_SELECTOR = "a.prod-thumb"
ALLOW_EMPTY_RESULTS = True

WATCHED_SLUGS = [
    "deltaetb",
]

STATE_FILE = Path(__file__).parent.parent / "coolshit_watchlist_state.json"


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _try_fetch_once() -> list[dict]:
    previous_state = _load_state()
    new_state = {}
    alerts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        page.goto(LISTING_URL, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.wait_for_selector(PRODUCT_CARD_SELECTOR, timeout=30000, state="attached")
        cards = page.query_selector_all(PRODUCT_CARD_SELECTOR)

        for card in cards:
            href = card.get_attribute("href") or ""
            slug = href.rstrip("/").split("/")[-1]
            if slug not in WATCHED_SLUGS:
                continue

            title = (card.get_attribute("title") or "").strip()
            card_text = card.inner_text().lower()

            if "coming soon" in card_text:
                status = "coming_soon"
            elif "sold out" in card_text:
                status = "sold_out"
            else:
                status = "available"

            price_el = card.query_selector(".prod-thumb-price span")
            price = price_el.inner_text().strip() if price_el else None
            product_url = href if href.startswith("http") else f"https://www.coolshit.co.nz{href}"

            prev_status = previous_state.get(slug)
            new_state[slug] = status

            if prev_status is not None and prev_status != status:
                alerts.append({
                    "id": f"{slug}::{status}",
                    "title": f"{title} (status: {status.replace('_', ' ')})",
                    "url": product_url,
                    "price": price,
                })

        browser.close()

    _save_state(new_state)
    return alerts


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Cool Shit Watchlist")
