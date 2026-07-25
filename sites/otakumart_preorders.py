"""
Otakumart - Pokemon TCG Pre-Orders. Shopify store, uses products.json,
scoped to their dedicated pre-order collection. Catches items the
moment they become available for pre-order, which may be earlier than
when they appear in the main Pokemon TCG collection.
"""

import requests
from sites.filters import is_tcg_product

SITE_NAME = "Otakumart - Pre-Orders"
BASE_URL = "https://otakumart.co.nz"
COLLECTION_HANDLE = "pre-order-pokemon-tcg"


def get_current_products() -> list[dict]:
    url = f"{BASE_URL}/collections/{COLLECTION_HANDLE}/products.json?limit=250"
    resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    data = resp.json()
    products = []
    for item in data.get("products", []):
        title = item.get("title", "")
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

ALLOW_EMPTY_RESULTS = True
