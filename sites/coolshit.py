"""
Cool Shit (coolshit.co.nz) - Pokemon TCG.
Each product is a single <a class="product-thumb" href="..." title="...">.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product

SITE_NAME = "Cool Shit - Pokemon"
LISTING_URL = "https://www.coolshit.co.nz/category/pokemon"
PRODUCT_CARD_SELECTOR = "a.prod-thumb"


def get_current_products() -> list[dict]:
    products = []

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
            products.append({"id": product_url, "title": title, "url": product_url, "price": None})
        browser.close()

    return products
