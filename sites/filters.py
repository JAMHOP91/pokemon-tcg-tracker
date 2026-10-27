"""
Shared filtering logic so all site scrapers only return actual TCG
card products - booster packs, elite trainer boxes, tins, blisters,
collections - and skip merch (mugs, plush, squishmallows, binders,
apparel, model kits, card holders), pre-constructed decks (Battle
Decks, Theme Decks, Tournament Decks, etc.), non-English releases,
non-TCG board games, live stream/card-break events, and specific
Japanese regional Pokemon Center collection boxes that keep flooding
alerts with price fluctuations.

Edit EXCLUDE_KEYWORDS to tune what gets filtered out. Matching is
case-insensitive and on whole words (plus an optional plural "s"), so
"hat" no longer catches "Hatterene" and "sleeve" no longer catches
"Sleeved Booster". ALLOW_PHRASES lets a specific phrase cancel ONE
exclusion (e.g. "poster collection" is a real TCG product, so it
cancels "poster") without weakening any other exclusion.

Run test_filters.py after any change here.
"""

import re

EXCLUDE_KEYWORDS = [
    "mug",
    "plush",
    "plushie",
    "squishmallow",
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
    # Specific deck types only - a bare "deck" would also drop real
    # products like the Premium Deck Set
    "battle deck",
    "tournament deck",
    "championships deck",
    "championship deck",
    "theme deck",
    "starter deck",
    "deck box",
    "deck case",
    "deck crafter",
    "japanese",
    "chinese",
    "korean",
    "battle academy",
    "board game",
    "stream",
    "livestream",
    "winner takes all",
    "energy",
    "energies",
    "card holder",
    "fukuoka",
    "hiroshima",
    "tohoku",
    "dice",
    "ticket",
]

# Phrase -> the single exclusion keyword it cancels
ALLOW_PHRASES = {
    "poster collection": "poster",
    "binder collection": "binder",
}


def _word_pattern(keyword: str) -> str:
    return r"\b" + re.escape(keyword) + r"s?\b"


def is_tcg_product(title: str) -> bool:
    """Returns True if the product title looks like an actual TCG
    card product (not merch, not a pre-con deck, not a non-English
    release, not a board game, not a live stream/break event, not a
    card storage accessory, not a Japanese regional collection box)."""
    for keyword in EXCLUDE_KEYWORDS:
        text = title
        # Blank out allowed phrases before checking the keyword they
        # cancel, so e.g. "Poster Collection" can't hide a separate
        # "Poster" elsewhere in the title
        for phrase, cancelled in ALLOW_PHRASES.items():
            if cancelled == keyword:
                text = re.sub(_word_pattern(phrase), " ", text, flags=re.I)
        if re.search(_word_pattern(keyword), text, re.I):
            return False
    return True
