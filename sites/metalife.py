"""
MetaLife - Pokemon TCG. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "MetaLife - Pokemon TCG"
BASE_URL = "https://www.metalife.co.nz"
COLLECTION_HANDLE = "pokemon-1"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"])

ALLOW_EMPTY_RESULTS = True
