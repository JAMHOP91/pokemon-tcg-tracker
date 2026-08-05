"""
Game Corner - Pokemon Pre-Orders. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Game Corner - Pokemon Pre-Orders"
BASE_URL = "https://gamecorner.co.nz"
COLLECTION_HANDLE = "pre-orders"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"])
