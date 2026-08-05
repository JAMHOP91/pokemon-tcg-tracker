"""
Shared helper for Shopify-based sites using the standard products.json
feed. Handles fetching, TCG filtering, keyword requirements, stock
filtering, and price extraction so individual site files just supply
their own URL/collection/keyword config instead of repeating this logic.
"""

import requests
from sites.filters import is_tcg_product


def get_shopify_products(base_url, collection_handle=None, require_keywords=None, scan_all_pages=False, max_pages=6):
    """
    Fetches Pokemon TCG products from a Shopify store.

    - collection_handle: scope to a specific collection (fast, preferred)
    - scan_all_pages: if True (no collection_handle), scans the general
      site-wide product feed across multiple pages instead, for stores
      with no dedicated collection
    - require_keywords: list of words that must ALL appear in the title
      (case-insensitive) - used for multi-TCG stores to exclude other games
    """
    products = []
    require_keywords = require_keywords or []

    if collection_handle:
        pages = [1]
        url_template = f"{base_url}/collections/{collection_handle}/products.json?limit=250&page={{page}}"
    else:
        pages = range(1, max_pages + 1)
        url_template = f"{base_url}/products.json?limit=250&page={{page}}"

    for page_num in pages:
        url = url_template.format(page=page_num)
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
        items = data.get("products", [])
        if not items:
            break

        for item in items:
            title = item.get("title", "")
            if not is_tcg_product(title):
                continue
            if any(kw.lower() not in title.lower() for kw in require_keywords):
                continue
            variants = item.get("variants", [])
            available_variants = [v for v in variants if v.get("available")]
            if not available_variants:
                continue
            cheapest = min(available_variants, key=lambda v: float(v.get("price", 0)))
            price = cheapest.get("price")
            handle = item.get("handle")
            product_url = f"{base_url}/products/{handle}"
            products.append({
                "id": str(item.get("id")),
                "title": title,
                "url": product_url,
                "price": f"${price}" if price else None,
            })

        if collection_handle or not scan_all_pages:
            break

    return products
