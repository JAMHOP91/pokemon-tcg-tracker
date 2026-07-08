"""
Watches Cool Shit's Pokemon listing for products marked "COMING SOON",
and alerts specifically when one of them loses that badge - i.e. it
just went live/became purchasable. Keeps its own small state file to
remember which products were "coming soon" last run.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from sites.filters import is_tcg_product

SITE_NAME = "Cool Shit - Coming Soon Watch"
LISTING_URL = "https://www.coolshit.co.nz/category/pokemon"
PRODUCT_CARD_SELECTOR = "a.prod-thumb"

STATE_FILE = Path(__file__).parent.parent / "coolshit_coming_soon_state.json"


def _load_coming_soon_ids() -> set:
    if not STATE_FILE.exists():
        return set()
    try:
        return set(json.loads(STATE_FILE.read_text(encoding="utf-8-sig")))
    except Exception:
        return set()


def _save_coming_soon_ids(ids: set) -> None:
    STATE_FILE.write_text(json.dumps(list(ids)))
