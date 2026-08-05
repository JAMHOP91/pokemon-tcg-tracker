"""
Cool Shit - Premium Collection Password Watch.

Watches the password-locked "Premium Collection" page and alerts the
moment it's no longer asking for a password. Only checks public page
text - never guesses, enters, or bypasses a password, never automates
any purchase. Uses the shared retry helper for resilience.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from sites.retry_helper import with_retries

SITE_NAME = "Cool Shit - Premium Collection Password Watch"
LOCKED_URL = "https://www.coolshit.co.nz/product/premiumcollection/locked"
UNLOCKED_URL = "https://www.coolshit.co.nz/product/premiumcollection"
ALLOW_EMPTY_RESULTS = True

STATE_FILE = Path(__file__).parent.parent / "coolshit_password_state.json"


def _load_was_locked() -> bool:
    if not STATE_FILE.exists():
        return True
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig")).get("locked", True)
    except Exception:
        return True


def _save_locked(locked: bool) -> None:
    STATE_FILE.write_text(json.dumps({"locked": locked}))


def _try_fetch_once() -> list[dict]:
    was_locked = _load_was_locked()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        page.goto(LOCKED_URL, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        page_text = page.inner_text("body").lower()
        currently_locked = "password required" in page_text or "password" in page_text
        browser.close()

    _save_locked(currently_locked)

    if was_locked and not currently_locked:
        return [{
            "id": "premiumcollection-unlocked",
            "title": "Cool Shit Premium Collection is now UNLOCKED",
            "url": UNLOCKED_URL,
            "price": None,
        }]

    return []


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Cool Shit Password Watch")
