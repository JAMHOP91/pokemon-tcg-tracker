"""
Sealed & Slabbed - Pokemon Sealed. Uses the shared Shopify helper,
scoped to their dedicated sealed-product-only collection.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Sealed & Slabbed - Pokemon Sealed"
BASE_URL = "https://sealedandslabbed.co.nz"
COLLECTION_HANDLE = "pokemon-sealed"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
