"""
Checks whether a product title matches any of the keywords in
priority_keywords.json - used to send a separate, louder alert for
specific sets/products someone is actively hunting for. Also checks
priority_exclude_keywords.json - a title matching an exclude term is
never treated as priority, even if it also matches an include keyword
(e.g. "Mega Evolution" stays priority generally, but specific sets
someone's already got can be excluded without losing future sets).
"""

import json
from pathlib import Path

KEYWORDS_FILE = Path(__file__).parent / "priority_keywords.json"
EXCLUDE_KEYWORDS_FILE = Path(__file__).parent / "priority_exclude_keywords.json"


def load_priority_keywords() -> list[str]:
    if not KEYWORDS_FILE.exists():
        return []
    return json.loads(KEYWORDS_FILE.read_text(encoding="utf-8-sig"))


def load_priority_exclude_keywords() -> list[str]:
    if not EXCLUDE_KEYWORDS_FILE.exists():
        return []
    return json.loads(EXCLUDE_KEYWORDS_FILE.read_text(encoding="utf-8-sig"))


def is_priority_product(title: str, keywords: list[str], exclude_keywords: list[str] = None) -> bool:
    title_lower = title.lower()
    exclude_keywords = exclude_keywords or []
    if any(ex.lower() in title_lower for ex in exclude_keywords):
        return False
    return any(keyword.lower() in title_lower for keyword in keywords)
