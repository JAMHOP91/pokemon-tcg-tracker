"""
Games Lab - Pokemon TCG. Custom platform, uses .grid-product__title-inner
for the title (confirmed via DevTools). Filtered to in-stock items via
the URL's own ?inventory=instock parameter, with a stock-text check as
a safety net. Uses shared retry helper.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product
from sites.retry_helper import with_retries

SITE_NAME = "Games Lab - Pokemon TCG"
LISTING_URL = "https://www.gameslab.co.nz/products/POKEMON-c164437144?inventory=instock"
TITLE_SELECTOR = ".grid-product__title-inner"


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
            if "sold out" in card_text or "out of stock" in card_text:
                continue

            seen_hrefs.add(href)
            product_url = href if href.startswith("http") else f"https://www.gameslab.co.nz{href}"
            price_el = card.query_selector(".grid-product__price")
            price = price_el.inner_text().strip() if price_el else None
            products.append({"id": product_url, "title": title, "url": product_url, "price": price})
        browser.close()

    return products


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Games Lab")
