"""
PlayX - Pokemon Pre-Orders. Uses the shared Shopify helper. Checks
BOTH their general pre-order collection AND the specific
"pokemon-2" collection used for the announced 30th Celebration
pre-order event (Aug 9, 2026).
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "PlayX - Pokemon Pre-Orders"
BASE_URL = "https://www.playx.co.nz"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    all_products = {}

    general = get_shopify_products(BASE_URL, collection_handle="pre-order", require_keywords=["pokemon"])
    for p in general:
        all_products[p["id"]] = p

    celebration = get_shopify_products(BASE_URL, collection_handle="pokemon-2")
    for p in celebration:
        all_products[p["id"]] = p

    return list(all_products.values())
