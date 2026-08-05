"""
The Game Tree NZ - Pokemon TCG. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "The Game Tree NZ"
BASE_URL = "https://thegametree.co.nz"
COLLECTION_HANDLE = "all"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"])
