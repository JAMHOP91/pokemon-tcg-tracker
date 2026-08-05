"""
Parko Cards - Pokemon TCG. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Parko Cards - Pokemon TCG"
BASE_URL = "https://parkocards.co.nz"
COLLECTION_HANDLE = "pokemon"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)

ALLOW_EMPTY_RESULTS = True
