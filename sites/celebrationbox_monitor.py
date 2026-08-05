"""
Broad web monitor for "Pokemon 30th Anniversary Celebration Box" (or
close variants) across ANY NZ retailer, not just tracked sites.
Uses a Google Alert (scoped to Region: New Zealand) delivered via
Kill the Newsletter as an RSS feed.

Keeps its OWN small state file (separate from the shared
seen_products.json) tracking which entry IDs have already been
alerted on, since the shared state mechanism was letting this specific
monitor's single recurring entry slip through repeatedly - likely from
local test runs having their fresh detection rolled back by routine
merge-conflict resolution before it properly propagated.
"""

import json
from pathlib import Path
import feedparser

SITE_NAME = "30th Celebration Box - Web Monitor"
GOOGLE_ALERTS_RSS_URL = "https://kill-the-newsletter.com/feeds/owdhr915nykcrg1q62ag.xml"
FEEDS = [
    ("Google Alerts", GOOGLE_ALERTS_RSS_URL),
]
REQUIRED_KEYWORDS = ["30th", "celebration"]
ALLOW_EMPTY_RESULTS = True

STATE_FILE = Path(__file__).parent.parent / "celebrationbox_seen_state.json"


def _load_seen() -> set:
    if not STATE_FILE.exists():
        return set()
    try:
        return set(json.loads(STATE_FILE.read_text(encoding="utf-8-sig")))
    except Exception:
        return set()


def _save_seen(seen: set) -> None:
    STATE_FILE.write_text(json.dumps(list(seen)))


def matches_target(text: str) -> bool:
    text_lower = text.lower()
    return all(keyword in text_lower for keyword in REQUIRED_KEYWORDS)


def get_current_products() -> list[dict]:
    already_seen = _load_seen()
    newly_seen = set(already_seen)
    products = []

    for source_name, feed_url in FEEDS:
        if not feed_url:
            continue
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            if not link or link in already_seen:
                continue
            if not matches_target(title) and not matches_target(summary):
                continue

            newly_seen.add(link)
            products.append({
                "id": link,
                "title": f"[{source_name}] {title}",
                "url": link,
                "price": None,
            })

    _save_seen(newly_seen)
    return products
