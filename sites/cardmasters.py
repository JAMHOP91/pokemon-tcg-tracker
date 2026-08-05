"""
Card Masters NZ - Pokemon TCG. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Card Masters NZ"
BASE_URL = "https://cardmasters.co.nz"
COLLECTION_HANDLE = "pokemon"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
