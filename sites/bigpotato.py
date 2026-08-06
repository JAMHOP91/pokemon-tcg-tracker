"""
Big Potato Collectibles - Pokemon Sealed. Runs on Wix, same standard
data-hook attributes confirmed on TCG NZ. Finds titles via the
confirmed data-hook="product-item-name", walks up to whichever link
wraps it, price via data-hook="product-item-price-to-pay". Uses
domcontentloaded + fixed wait instead of networkidle (Wix background
activity can prevent networkidle from resolving). Uses shared retry.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product
from sites.retry_helper import with_retries

SITE_NAME = "Big Potato Collectibles - Pokemon Sealed"
LISTING_URL = "https://www.bigpotato.co.nz/pokemonsealedcollection"
TITLE_SELECTOR = '[data-hook="product-item-name"]'


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
            if "out of stock" in card_text or "sold out" in card_text:
                continue

            seen_hrefs.add(href)
            product_url = href if href.startswith("http") else f"https://www.bigpotato.co.nz{href}"
            price_el = card.query_selector('[data-hook="product-item-price-to-pay"]')
            price = price_el.inner_text().strip() if price_el else None
            products.append({"id": product_url, "title": title, "url": product_url, "price": price})
        browser.close()

    return products


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Big Potato Collectibles")
