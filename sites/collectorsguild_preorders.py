"""
Collectors Guild - Pokemon Pre-Orders. Uses the shared Shopify helper.
Includes sold-out items - see Otakumart pre-orders for rationale.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Collectors Guild - Pokemon Pre-Orders"
BASE_URL = "https://collectorsguild.co.nz"
COLLECTION_HANDLE = "pokemon-pre-orders"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, include_sold_out=True)
