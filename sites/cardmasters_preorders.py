"""
Card Masters - Pre-Orders. Uses the shared Shopify helper.
Includes sold-out items - see Otakumart pre-orders for rationale.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Card Masters - Pre-Orders"
BASE_URL = "https://cardmasters.co.nz"
COLLECTION_HANDLE = "pre-orders"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"], include_sold_out=True)
