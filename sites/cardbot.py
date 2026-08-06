"""
Card Bot - English Pokemon TCG. Uses the shared Shopify helper, scoped
to their dedicated English-only collection (they separately stock
Japanese/Chinese, which is intentionally excluded here).
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Card Bot - English Pokemon TCG"
BASE_URL = "https://cardbot.co.nz"
COLLECTION_HANDLE = "english-pokemon-tcg"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
