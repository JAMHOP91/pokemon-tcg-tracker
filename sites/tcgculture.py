"""
TCG Culture - Pokemon. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "TCG Culture - Pokemon"
BASE_URL = "https://tcgculture.com"
COLLECTION_HANDLE = "pokemon"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"])

ALLOW_EMPTY_RESULTS = True
