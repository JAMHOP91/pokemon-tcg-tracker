"""
Pop Stop - Pokemon TCG. Uses the shared Shopify helper, but scoped to
the general /collections/pokemon page (mixes TCG with Pop! Vinyls,
plush, manga, posters), so requires TCG-specific keywords in the title.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Pop Stop - Pokemon TCG"
BASE_URL = "https://popstop.co.nz"
COLLECTION_HANDLE = "pokemon"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    products = get_shopify_products(BASE_URL, collection_handle=COLLECTION_HANDLE)
    return [
        p for p in products
        if "tcg" in p["title"].lower() or "booster" in p["title"].lower() or "elite trainer" in p["title"].lower()
    ]
