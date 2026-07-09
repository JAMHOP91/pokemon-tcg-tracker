"""
Broad web monitor for "Pokemon 30th Anniversary Celebration Box" (or
close variants) across ANY NZ retailer, not just tracked sites.

Uses a Google Alert (scoped to Region: New Zealand) delivered via
Kill the Newsletter as an RSS feed. Fill in GOOGLE_ALERTS_RSS_URL
once that's set up.
"""

import feedparser

SITE_NAME = "30th Celebration Box - Web Monitor"

GOOGLE_ALERTS_RSS_URL = ""

FEEDS = [
    ("Google Alerts", GOOGLE_ALERTS_RSS_URL),
]

REQUIRED_KEYWORDS = ["30th", "celebration"]


def matches_target(text: str) -> bool:
    text_lower = text.lower()
    return all(keyword in text_lower for keyword in REQUIRED_KEYWORDS)


def get_current_products() -> list[dict]:
    products = []
    seen_links = set()

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

            if not link or link in seen_links:
                continue
            if not matches_target(title) and not matches_target(summary):
                continue

            seen_links.add(link)
            products.append({
                "id": link,
                "title": f"[{source_name}] {title}",
                "url": link,
                "price": None,
            })

    return products

ALLOW_EMPTY_RESULTS = True
