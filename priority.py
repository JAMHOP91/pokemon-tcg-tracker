"""
Checks whether a product title matches any of the keywords in
priority_keywords.json - used to send a separate, louder alert for
specific sets/products someone is actively hunting for.
"""

import json
from pathlib import Path

KEYWORDS_FILE = Path(__file__).parent / "priority_keywords.json"


def load_priority_keywords() -> list[str]:
    if not KEYWORDS_FILE.exists():
        return []
    return json.loads(KEYWORDS_FILE.read_text(encoding="utf-8-sig"))


def is_priority_product(title: str, keywords: list[str]) -> bool:
    title_lower = title.lower()
    return any(keyword.lower() in title_lower for keyword in keywords)
