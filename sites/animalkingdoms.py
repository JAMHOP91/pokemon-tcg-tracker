"""
Animal Kingdoms - Pokemon TCG. Uses the shared Shopify helper. General
toy store (mostly Schleich/Playmobil/Sylvanian Families), so requires
"pokemon" explicitly in the title as a safety net.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Animal Kingdoms - Pokemon TCG"
BASE_URL = "https://animalkingdoms.co.nz"
COLLECTION_HANDLE = "pokemon-tcg"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE, require_keywords=["pokemon"])
