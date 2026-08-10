"""
Shared filtering logic so all site scrapers only return actual TCG
card products - booster packs, elite trainer boxes, tins, blisters,
collections - and skip merch (mugs, plush, binders, apparel, model
kits), pre-constructed decks (Battle Decks, Theme Decks, Tournament
Decks, etc.), and non-English releases.

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
    "pin collection",
    "stationery",
    "notebook",
    "nanoblock",
    "acrylic",
    "riftbound",
    "league of legends",
    "protector",
    "4d build",
    "model kit",
    "puzzle",
    "deck",
    "japanese",
    "chinese",
    "korean",
]


def is_tcg_product(title: str) -> bool:
    """Returns True if the product title looks like an actual TCG
    card product (not merch, not a pre-con deck, not a non-English
    release)."""
    title_lower = title.lower()
    return not any(keyword in title_lower for keyword in EXCLUDE_KEYWORDS)
