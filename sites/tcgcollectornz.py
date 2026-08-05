"""
TCG Collector NZ - Pokemon TCG. Uses the shared Shopify helper.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "TCG Collector NZ"
BASE_URL = "https://tcgcollectornz.com"
COLLECTION_HANDLE = "pokemon-tcg-collector-nz"


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
