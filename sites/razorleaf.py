"""
Razor Leaf - Pokemon TCG. Uses the shared Shopify helper. This store
organizes collections by individual set (no single "all Pokemon"
catch-all), so this checks their two broadest collections instead -
Elite Trainer Boxes and Booster Boxes, spanning all sets for those
product types.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Razor Leaf - Pokemon TCG"
BASE_URL = "https://www.razorleaf.co.nz"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    all_products = {}

    etbs = get_shopify_products(BASE_URL, collection_handle="elite-trainer-boxes")
    for p in etbs:
        all_products[p["id"]] = p

    boosters = get_shopify_products(BASE_URL, collection_handle="booster-boxes")
    for p in boosters:
        all_products[p["id"]] = p

    return list(all_products.values())
