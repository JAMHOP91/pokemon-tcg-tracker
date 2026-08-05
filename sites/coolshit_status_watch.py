"""
Cool Shit - Status Watch.

Tracks EVERY product's status (coming_soon / available / sold_out) and
title, not just ones explicitly marked "coming soon". Alerts on any
meaningful change - a status flip, OR a title change on a URL we'd
already seen. Uses the shared retry helper for resilience.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product
from sites.retry_helper import with_retries

SITE_NAME = "Cool Shit - Status Watch"
LISTING_URL = "https://www.coolshit.co.nz/category/pokemon"
PRODUCT_CARD_SELECTOR = "a.prod-thumb"
ALLOW_EMPTY_RESULTS = True

STATE_FILE = Path(__file__).parent.parent / "coolshit_status_state.json"


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
            title = (card.get_attribute("title") or "").strip()
            href = card.get_attribute("href")
            if not title or not href:
                continue
            if not is_tcg_product(title):
                continue

            product_url = href if href.startswith("http") else f"https://www.coolshit.co.nz{href}"
            card_text = card.inner_text().lower()

            if "coming soon" in card_text:
                status = "coming_soon"
            elif "sold out" in card_text:
                status = "sold_out"
            else:
                status = "available"

            price_el = card.query_selector(".prod-thumb-price span")
            price = price_el.inner_text().strip() if price_el else None

            new_state[product_url] = {"title": title, "status": status}

            prev = previous_state.get(product_url)
            if prev is None:
                if status != "coming_soon":
                    alerts.append({
                        "id": f"{product_url}::{status}",
                        "title": f"{title} (new listing - {status.replace('_', ' ')})",
                        "url": product_url,
                        "price": price,
                    })
            else:
                status_changed = prev.get("status") != status
                title_changed = prev.get("title") != title
                if status_changed or title_changed:
                    alerts.append({
                        "id": f"{product_url}::{status}::{title}",
                        "title": f"{title} (status: {status.replace('_', ' ')})",
                        "url": product_url,
                        "price": price,
                    })

        browser.close()

    _save_state(new_state)
    return alerts


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Cool Shit Status Watch")
