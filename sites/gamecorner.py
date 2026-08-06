"""
Game Corner - Pokemon. Uses the shared Shopify helper, scoped to their
general Pokemon collection (regular stock, separate from pre-orders).
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Game Corner - Pokemon"
BASE_URL = "https://gamecorner.co.nz"
COLLECTION_HANDLE = "pokemon"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
