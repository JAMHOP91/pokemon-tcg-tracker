"""
Otakumart - Pokemon TCG. Shopify store, uses products.json, scoped to their pokemon-tcg collection.
"""

import requests
from sites.filters import is_tcg_product

SITE_NAME = "Otakumart - Pokemon TCG"
BASE_URL = "https://otakumart.co.nz"
COLLECTION_HANDLE = "pokemon-tcg"


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
        handle = item.get("handle")
        product_url = f"{BASE_URL}/products/{handle}"
        price = None
        variants = item.get("variants", [])
        if variants:
            price = variants[0].get("price")
        products.append({"id": str(item.get("id")), "title": title, "url": product_url, "price": f"${price}" if price else None})
    return products
