"""
Cardtopia NZ - Pokemon TCG. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Cardtopia NZ"
BASE_URL = "https://www.cardtopia.co.nz"
COLLECTION_HANDLE = "new-arrivals"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"])
