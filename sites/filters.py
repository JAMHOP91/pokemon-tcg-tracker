"""
Shared filtering logic so all site scrapers only return actual TCG
card products — booster packs, elite trainer boxes, tins, decks,
blisters, collections — and skip merch like mugs, plush, binders,
posters, apparel, etc.

Edit EXCLUDE_KEYWORDS to tune what gets filtered out. Matching is
case-insensitive and checks if the keyword appears anywhere in the title.
"""

EXCLUDE_KEYWORDS = [
    "mug",
    "plush",
    "binder",
    "portfolio",
    "backpack",
    "hoodie",
    "t-shirt",
    "tshirt",
    "shirt",
    "poster",
    "keychain",
    "funko",
    "sticker sheet",
    "monopoly",
    "playmat",
    "sleeve",
    "toploader",
    "top loader",
    "figure",
    "figurine",
    "apparel",
    "cap",
    "hat",
    "bag",
    "case",
    "pin collection",
    "stationery",
    "notebook",
]


def is_tcg_product(title: str) -> bool:
    """Returns True if the product title looks like an actual TCG
    card product (not merch)."""
    title_lower = title.lower()
    return not any(keyword in title_lower for keyword in EXCLUDE_KEYWORDS)