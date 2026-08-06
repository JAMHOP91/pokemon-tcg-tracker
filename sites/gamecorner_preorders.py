"""
Game Corner - Pokemon Pre-Orders. Uses the shared Shopify helper,
scoped to their dedicated Pokemon-specific pre-orders collection
(more accurate than the generic multi-TCG pre-orders collection).
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Game Corner - Pokemon Pre-Orders"
BASE_URL = "https://gamecorner.co.nz"
COLLECTION_HANDLE = "pkmn-pre-orders"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
