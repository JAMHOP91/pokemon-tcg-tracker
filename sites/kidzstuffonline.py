"""
Kidzstuffonline - Pokemon TCG. Uses the shared Shopify helper in
general-scan mode, since there's no dedicated Pokemon collection.
"""

from sites.shopify_helper import get_shopify_products

SITE_NAME = "Kidzstuffonline - Pokemon TCG"
BASE_URL = "https://kidzstuffonline.co.nz"
ALLOW_EMPTY_RESULTS = True


def get_current_products() -> list[dict]:
    return get_shopify_products(BASE_URL, scan_all_pages=True, require_keywords=["pokemon", "tcg"])
