"""
Sends a weekly summary of everything the tracker found in the last 7
days - a consolidated digest as a safety net in case any individual
live alert was missed, and a nice weekly snapshot of activity.
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from notify import send_telegram_message

HISTORY_FILE = Path(__file__).parent / "release_history.json"


def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return []


def main():
    history = load_history()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)

    recent = [h for h in history if datetime.fromisoformat(h["timestamp"]) >= cutoff]

    if not recent:
        send_telegram_message("WEEKLY DIGEST: No new products found this week.")
        return

    by_site = {}
    priority_count = 0
    for item in recent:
        by_site.setdefault(item["site"], []).append(item)
        if item.get("priority"):
            priority_count += 1

    lines = [f"WEEKLY DIGEST: {len(recent)} item(s) found across {len(by_site)} site(s) this week"]
    if priority_count:
        lines.append(f"({priority_count} were priority matches)")
    lines.append("")

    for site_name, items in sorted(by_site.items(), key=lambda x: -len(x[1])):
        lines.append(f"{site_name}: {len(items)}")

    send_telegram_message("\n".join(lines))


if __name__ == "__main__":
    main()
