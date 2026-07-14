"""
JB Hi-Fi NZ - Pokemon TCG.
Finds product links by URL pattern and reads title from image alt text.

JB Hi-Fi's bot protection appears to intermittently block requests from
cloud/datacenter IPs (like GitHub Actions uses) more than home connections,
so this retries a couple of times with fresh browser sessions before
giving up, rather than failing on the first block.
"""

import time
from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product

SITE_NAME = "JB Hi-Fi NZ"
LISTING_URL = "https://www.jbhifi.co.nz/collections/collectibles-merchandise/pokemon-trading-cards"
PRODUCT_LINK_SELECTOR = 'a[href*="/products/"]'
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
            product_url = href if href.startswith("http") else f"https://www.jbhifi.co.nz{href}"
            price_el = link.query_selector('[data-testid="ticket-price"]')
            price = price_el.inner_text().strip() if price_el else None
            products.append({"id": product_url, "title": title, "url": product_url, "price": f"${price}" if price else None})
        browser.close()

    return products


def get_current_products() -> list[dict]:
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return _try_fetch_once()
        except Exception as e:
            last_error = e
            print(f"  JB Hi-Fi attempt {attempt}/{MAX_ATTEMPTS} failed: {e}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    raise last_error

ZERO_STREAK_THRESHOLD_OVERRIDE = 10
