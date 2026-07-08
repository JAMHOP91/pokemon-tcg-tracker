"""
Watches Cool Shit's Pokemon listing for products marked "COMING SOON",
and alerts specifically when one of them loses that badge - i.e. it
just went live/became purchasable. Keeps its own small state file to
remember which products were "coming soon" last run.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product

SITE_NAME = "Cool Shit - Coming Soon Watch"
LISTING_URL = "https://www.coolshit.co.nz/category/pokemon"
PRODUCT_CARD_SELECTOR = "a.prod-thumb"

STATE_FILE = Path(__file__).parent.parent / "coolshit_coming_soon_state.json"


def _load_coming_soon_ids() -> set:
    if not STATE_FILE.exists():
        return set()
    try:
        return set(json.loads(STATE_FILE.read_text(encoding="utf-8-sig")))
    except Exception:
        return set()


def _save_coming_soon_ids(ids: set) -> None:
    STATE_FILE.write_text(json.dumps(list(ids)))


def get_current_products() -> list[dict]:
    previously_coming_soon = _load_coming_soon_ids()
    currently_coming_soon = set()
    newly_available = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        page.goto(LISTING_URL, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)
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
                currently_coming_soon.add(product_url)
            elif product_url in previously_coming_soon:
                price_el = card.query_selector(".prod-thumb-price span")
                price = price_el.inner_text().strip() if price_el else None
                newly_available.append({"id": product_url, "title": title, "url": product_url, "price": price})

        browser.close()

    _save_coming_soon_ids(currently_coming_soon)
    return newly_available
