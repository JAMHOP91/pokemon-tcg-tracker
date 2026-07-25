"""
Game Corner - Pokemon Pre-Orders. Shopify store, uses products.json.
They sell multiple TCGs (MTG, One Piece, Lorcana, etc.) in the same
pre-orders collection, so this explicitly requires "pokemon" in the title.
"""

import requests
from sites.filters import is_tcg_product

SITE_NAME = "Game Corner - Pokemon Pre-Orders"
BASE_URL = "https://gamecorner.co.nz"
COLLECTION_HANDLE = "pre-orders"


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
        if "pokemon" not in title.lower() and "pokémon" not in title.lower():
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
