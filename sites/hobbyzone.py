"""
Hobby Zone - Pokemon Cards. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Hobby Zone - Pokemon Cards"
BASE_URL = "https://hobbyzone.co.nz"
COLLECTION_HANDLE = "pokemon-cards"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)

ALLOW_EMPTY_RESULTS = True
