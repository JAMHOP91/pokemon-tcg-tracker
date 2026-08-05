"""
Hobby Lords - Pokemon TCG.
Product links follow /products/single/... Title comes from the product
image's alt attribute. Uses the shared retry helper for resilience.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product
from sites.retry_helper import with_retries

SITE_NAME = "Hobby Lords - Pokemon"
LISTING_URL = "https://www.hobbylords.co.nz/shop/brand/pokemon"
PRODUCT_LINK_SELECTOR = 'a[href*="/products/single/"]'


def _try_fetch_once() -> list[dict]:
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
            product_url = href if href.startswith("http") else f"https://www.hobbylords.co.nz{href}"
            products.append({"id": product_url, "title": title, "url": product_url, "price": None})
        browser.close()

    return products


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Hobby Lords")
