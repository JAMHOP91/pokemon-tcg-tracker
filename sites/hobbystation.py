"""
Hobby Station - Pokemon TCG. Custom platform, not Shopify.
Each product sits in a .prod-item div, with the title/link in
h4.prod-name a and price in .prod-price. The .prod-item class appears
to be used site-wide (including recommendation widgets), so this
requires "pokemon" explicitly in the title. Uses the shared retry helper.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product
from sites.retry_helper import with_retries

SITE_NAME = "Hobby Station - Pokemon TCG"
LISTING_URL = "https://hobbystation.co.nz/pokemon-tcg/"
CARD_SELECTOR = ".prod-item"
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
        page.wait_for_selector(CARD_SELECTOR, timeout=30000, state="attached")
        cards = page.query_selector_all(CARD_SELECTOR)
        for card in cards:
            title_el = card.query_selector("h4.prod-name a")
            if not title_el:
                continue
            title = title_el.inner_text().strip()
            if not title or not is_tcg_product(title):
                continue
            if "pokemon" not in title.lower() and "pokémon" not in title.lower():
                continue

            href = title_el.get_attribute("href")
            if not href or href in seen_hrefs:
                continue

            card_text = card.inner_text().lower()
            if "out of stock" in card_text or "sold out" in card_text:
                continue

            seen_hrefs.add(href)
            product_url = href if href.startswith("http") else f"https://hobbystation.co.nz{href}"
            price_el = card.query_selector(".prod-price")
            price = price_el.inner_text().strip() if price_el else None
            products.append({"id": product_url, "title": title, "url": product_url, "price": price})
        browser.close()

    return products


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Hobby Station")
