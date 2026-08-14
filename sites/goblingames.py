"""
Goblin Games NZ - Pokemon TCG Sealed Packs. Uses the shared Shopify
helper, scoped to their dedicated sealed-product-only collection.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Goblin Games NZ - Pokemon TCG"
BASE_URL = "https://goblingames.nz"
COLLECTION_HANDLE = "pokemon-tcg-sealed-packs"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
