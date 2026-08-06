"""
Cool Shit - Password Watch List.

Watches a LIST of password-locked product pages and alerts the moment
any of them stop asking for a password. Add a new slug to
WATCHED_SLUGS whenever you spot a new password-gated 30th Celebration
item (the slug is the last part of the product URL, e.g. for
"coolshit.co.nz/product/celebration" the slug is "celebration").

Only checks each page's own public text (whether it says "password
required"). Never guesses, enters, or bypasses a password, never
automates any purchase.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from sites.retry_helper import with_retries

SITE_NAME = "Cool Shit - Password Watch"
ALLOW_EMPTY_RESULTS = True

WATCHED_SLUGS = [
    "premiumcollection",
    "celebration",
    "knockout",
    "techsticker",
]

STATE_FILE = Path(__file__).parent.parent / "coolshit_password_state.json"


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state))


def _try_fetch_once() -> list[dict]:
    old_state = _load_state()
    new_state = {}
    alerts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )

        for slug in WATCHED_SLUGS:
            locked_url = f"https://www.coolshit.co.nz/product/{slug}/locked"
            unlocked_url = f"https://www.coolshit.co.nz/product/{slug}"
            was_locked = old_state.get(slug, True)

            try:
                page.goto(locked_url, timeout=20000, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                page_text = page.inner_text("body").lower()
                currently_locked = "password required" in page_text or "password" in page_text
            except Exception:
                currently_locked = was_locked

            new_state[slug] = currently_locked

            if was_locked and not currently_locked:
                alerts.append({
                    "id": f"{slug}-unlocked",
                    "title": f"Cool Shit '{slug}' is now UNLOCKED",
                    "url": unlocked_url,
                    "price": None,
                })

        browser.close()

    _save_state(new_state)
    return alerts


def get_current_products() -> list[dict]:
    return with_retries(_try_fetch_once, "Cool Shit Password Watch")
