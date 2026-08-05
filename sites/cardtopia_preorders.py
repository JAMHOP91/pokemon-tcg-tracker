"""
Cardtopia - Pre-Orders. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Cardtopia - Pre-Orders"
BASE_URL = "https://www.cardtopia.co.nz"
COLLECTION_HANDLE = "pokemon-english-pre-orders"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
