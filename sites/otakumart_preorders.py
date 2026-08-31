"""
Otakumart - Pokemon TCG Pre-Orders. Uses the shared Shopify helper.
Includes sold-out items - a listing existing at all on a pre-order
page is the valuable signal, since hyped items can sell out within
minutes of appearing.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Otakumart - Pre-Orders"
BASE_URL = "https://otakumart.co.nz"
COLLECTION_HANDLE = "pre-order-pokemon-tcg"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, include_sold_out=True)
