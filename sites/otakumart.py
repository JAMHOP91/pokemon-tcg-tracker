"""
Otakumart - Pokemon TCG. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Otakumart - Pokemon TCG"
BASE_URL = "https://otakumart.co.nz"
COLLECTION_HANDLE = "pokemon-tcg"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
