"""
Redline Trading - English Pokemon TCG. Uses the shared Shopify helper,
scoped to their English-only collection (they separately stock
Japanese, which is intentionally excluded here).
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Redline Trading - English Pokemon TCG"
BASE_URL = "https://redlinetrading.co.nz"
COLLECTION_HANDLE = "english"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"])
