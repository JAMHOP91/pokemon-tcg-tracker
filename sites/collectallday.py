"""
Collect All Day - Pokemon TCG. Runs on Squarespace. Uses their "/new"
page which lists recently added products across all categories.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product

SITE_NAME = "Collect All Day"
LISTING_URL = "https://www.collectallday.com/new"
PRODUCT_CARD_SELECTOR = "a.product"


def get_current_products() -> list[dict]:
    products = []
    seen_hrefs = set()

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
            href = card.get_attribute("href")
            if not href or href in seen_hrefs:
                continue
            title_el = card.query_selector(".product-title")
            if not title_el:
                continue
            title = title_el.inner_text().strip()
            if not title or not is_tcg_product(title):
                continue
            card_text = card.inner_text().lower()
            if "sold out" in card_text:
                continue
            seen_hrefs.add(href)
            product_url = href if href.startswith("http") else f"https://www.collectallday.com{href}"
            price_el = card.query_selector(".product-price")
            price = price_el.inner_text().strip() if price_el else None
            products.append({"id": product_url, "title": title, "url": product_url, "price": price})
        browser.close()

    return products
