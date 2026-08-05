"""
Turtle Island - Pokemon TCG Pre-Orders. Custom platform using Tailwind
utility classes, so this finds products by URL pattern (/product/...)
instead, reading the title from the link's own text. Uses the shared
retry helper for resilience.
"""

import re
from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product
from sites.retry_helper import with_retries

SITE_NAME = "Turtle Island - Pokemon Pre-Orders"
LISTING_URL = "https://turtleisland.co.nz/collection/pre-order"
PRODUCT_LINK_SELECTOR = 'a[href*="/product/"]'
ALLOW_EMPTY_RESULTS = True


def _try_fetch_once() -> list[dict]:
    products = []
    seen_hrefs = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        page.goto(LISTING_URL, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.wait_for_selector(PRODUCT_LINK_SELECTOR, timeout=30000, state="attached")
        links = page.query_selector_all(PRODUCT_LINK_SELECTOR)
        for link in links:
            title = link.inner_text().strip()
            href = link.get_attribute("href")
            if not title or not href or href in seen_hrefs:
                continue
            if not is_tcg_product(title):
                continue
            if "pokemon" not in title.lower() and "pokémon" not in title.lower():
                continue

            card_handle = link.evaluate_handle("el => el.closest('li')")
            card = card_handle.as_element()
            card_text = card.inner_text().lower() if card else ""
            if "sold out" in card_text:
                continue

            seen_hrefs.add(href)
            product_url = href if href.startswith("http") else f"https://turtleisland.co.nz{href}"
            price_match = re.search(r"\$[\d,]+\.\d{2}", card_text) if card else None
            price = price_match.group(0) if price_match else None
            products.append({"id": product_url, "title": title, "url": product_url, "price": price})
        browser.close()

    return products


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Turtle Island")
