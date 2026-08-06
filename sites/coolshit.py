"""
Cool Shit (coolshit.co.nz) - Pokemon TCG.
Checks BOTH the dedicated /category/pokemon page AND the general
/products page, since some Pokemon items occasionally only show up
on one or the other (miscategorized). Requires "pokemon" in the title
for items sourced from the general page to avoid picking up unrelated
merch. Skips sold-out items. Uses the shared retry helper.
"""

from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product
from sites.retry_helper import with_retries

SITE_NAME = "Cool Shit - Pokemon"
LISTING_URLS = [
    "https://www.coolshit.co.nz/category/pokemon",
    "https://www.coolshit.co.nz/products",
]
PRODUCT_CARD_SELECTOR = "a.prod-thumb"


def _scrape_page(page, url, require_pokemon_keyword):
    products = []
    page.goto(url, timeout=30000)
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
        if require_pokemon_keyword and "pokemon" not in title.lower() and "pokémon" not in title.lower():
            continue
        card_text = card.inner_text().lower()
        if "sold out" in card_text:
            continue
        product_url = href if href.startswith("http") else f"https://www.coolshit.co.nz{href}"
        price_el = card.query_selector(".prod-thumb-price span")
        price = price_el.inner_text().strip() if price_el else None
        products.append({"id": product_url, "title": title, "url": product_url, "price": price})
    return products


def _try_fetch_once() -> list[dict]:
    all_products = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )

        category_products = _scrape_page(page, LISTING_URLS[0], require_pokemon_keyword=False)
        for p_item in category_products:
            all_products[p_item["id"]] = p_item

        general_products = _scrape_page(page, LISTING_URLS[1], require_pokemon_keyword=True)
        for p_item in general_products:
            if p_item["id"] not in all_products:
                all_products[p_item["id"]] = p_item

        browser.close()

    return list(all_products.values())


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Cool Shit")
