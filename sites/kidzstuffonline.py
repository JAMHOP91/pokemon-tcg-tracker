"""
Kidzstuffonline - Pokemon TCG. Shopify store, general toy shop with no
dedicated Pokemon collection, so this scans their general products.json
feed (a few pages, since they sell a lot of unrelated toys) and filters
to titles that actually mention Pokemon TCG.
"""

import requests
from sites.filters import is_tcg_product

SITE_NAME = "Kidzstuffonline - Pokemon TCG"
BASE_URL = "https://kidzstuffonline.co.nz"
MAX_PAGES = 6
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    products = []
    for page_num in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}/products.json?limit=250&page={page_num}"
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
        items = data.get("products", [])
        if not items:
            break

        for item in items:
            title = item.get("title", "")
            if "pokemon" not in title.lower() and "pokémon" not in title.lower():
                continue
            if "tcg" not in title.lower():
                continue
            if not is_tcg_product(title):
                continue
            variants = item.get("variants", [])
            available_variants = [v for v in variants if v.get("available")]
            if not available_variants:
                continue
            cheapest = min(available_variants, key=lambda v: float(v.get("price", 0)))
            price = cheapest.get("price")
            handle = item.get("handle")
            product_url = f"{BASE_URL}/products/{handle}"
            products.append({"id": str(item.get("id")), "title": title, "url": product_url, "price": f"${price}" if price else None})

    return products
    for page_num in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}/products.json?limit=250&page={page_num}"
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
        items = data.get("products", [])
        if not items:
            break

        for item in items:
            title = item.get("title", "")
            if "pokemon" not in title.lower() and "pokémon" not in title.lower():
                continue
            if "tcg" not in title.lower():
                continue
            if not is_tcg_product(title):
                continue
            variants = item.get("variants", [])
            available_variants = [v for v in variants if v.get("available")]
            if not available_variants:
                continue
            cheapest = min(available_variants, key=lambda v: float(v.get("price", 0)))
            price = cheapest.get("price")
            handle = item.get("handle")
            product_url = f"{BASE_URL}/products/{handle}"
            products.append({"id": str(item.get("id")), "title": title, "url": product_url, "price": f"${price}" if price else None})

    return products
