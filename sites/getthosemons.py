"""
GetThoseMons - Sealed Pokemon TCG. Uses the shared Shopify helper,
scoped specifically to their sealed-product collection (they're
primarily a singles/trade-in marketplace, so this avoids the noise
of individual card listings).
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "GetThoseMons - Sealed Pokemon TCG"
BASE_URL = "https://getthosemons.co.nz"
COLLECTION_HANDLE = "all-pokemon-trading-card-game-sealed"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
