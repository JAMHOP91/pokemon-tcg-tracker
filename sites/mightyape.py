"""
Mighty Ape NZ - Pokemon TCG.
Finds product links by URL pattern and reads title from image alt text.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product

SITE_NAME = "Mighty Ape - Pokemon TCG"
LISTING_URL = "https://www.mightyape.co.nz/hobbies/trading-cards/pokemon/all"
PRODUCT_LINK_SELECTOR = 'a[href*="/mn/buy/"]'


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
        page.wait_for_selector(PRODUCT_LINK_SELECTOR, timeout=30000, state="attached")
        links = page.query_selector_all(PRODUCT_LINK_SELECTOR)
        for link in links:
            href = link.get_attribute("href")
            if not href or href in seen_hrefs:
                continue
            img = link.query_selector("img[alt]")
            if not img:
                continue
            title = (img.get_attribute("alt") or "").strip()
            if not title:
                continue
            if not is_tcg_product(title):
                continue
            seen_hrefs.add(href)
            product_url = href if href.startswith("http") else f"https://www.mightyape.co.nz{href}"
            products.append({"id": product_url, "title": title, "url": product_url, "price": None})
        browser.close()

    return products
