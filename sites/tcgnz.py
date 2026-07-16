"""
TCG NZ - Pokemon TCG. Runs on Wix. Finds products by the confirmed
data-hook="product-item-name" title element, then walks up to whichever
link wraps it (avoids depending on guessing the wrapper's exact name).

Retries a couple of times before giving up, since Wix sites can be
slow to fully render on a given attempt.
"""

import time
from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product

SITE_NAME = "TCG NZ"
LISTING_URL = "https://www.tcgnz.co.nz/shop-collection"
TITLE_SELECTOR = '[data-hook="product-item-name"]'
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 10


def _try_fetch_once() -> list[dict]:
    products = []
    seen_hrefs = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        page.goto(LISTING_URL, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)
        page.wait_for_selector(TITLE_SELECTOR, timeout=30000, state="attached")
        titles = page.query_selector_all(TITLE_SELECTOR)
        for title_el in titles:
            title = title_el.inner_text().strip()
            if not title or not is_tcg_product(title):
                continue

            card_handle = title_el.evaluate_handle("el => el.closest('a')")
            card = card_handle.as_element()
            if not card:
                continue

            href = card.get_attribute("href")
            if not href or href in seen_hrefs:
                continue

            card_text = card.inner_text().lower()
            if "out of stock" in card_text:
                continue

            seen_hrefs.add(href)
            product_url = href if href.startswith("http") else f"https://www.tcgnz.co.nz{href}"
            price_el = card.query_selector('[data-hook="product-item-price-to-pay"]')
            price = price_el.inner_text().strip() if price_el else None
            products.append({"id": product_url, "title": title, "url": product_url, "price": price})
        browser.close()

    return products


def get_current_products() -> list[dict]:
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return _try_fetch_once()
        except Exception as e:
            last_error = e
            print(f"  TCG NZ attempt {attempt}/{MAX_ATTEMPTS} failed: {e}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    raise last_error
