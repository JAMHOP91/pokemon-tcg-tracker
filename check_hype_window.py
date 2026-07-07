"""
Checks whether today's date (UTC) falls inside any window listed in
hype_windows.json. Prints "true" or "false" - used by the fast-polling
GitHub Actions workflow to decide whether to actually run the scrapers.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

WINDOWS_FILE = Path(__file__).parent / "hype_windows.json"


def main():
    if not WINDOWS_FILE.exists():
        print("false")
        return

    windows = json.loads(WINDOWS_FILE.read_text(encoding="utf-8-sig"))
    today = datetime.now(timezone.utc).date()

    for w in windows:
        start = datetime.strptime(w["start"], "%Y-%m-%d").date()
        end = datetime.strptime(w["end"], "%Y-%m-%d").date()
        if start <= today <= end:
            print("true")
            return

    print("false")


if __name__ == "__main__":
    main()
