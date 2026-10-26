"""
Merges seen_products.json between the current local state and whatever
is on origin/main, combining (union) the "seen_ids" lists AND the
"prices" dictionaries per site, rather than picking one side entirely.
This prevents a merge conflict from ever accidentally discarding
recently-seen products or recently-recorded prices, which was causing
already-notified items (and already-reported price drops) to reappear
and re-trigger duplicate Telegram alerts.

"last_seen" (product id -> ISO timestamp) is merged per id, keeping the
newer timestamp. Ids last seen more than GRACE_MINUTES before the site's
latest successful run are then dropped from both last_seen and
seen_ids - otherwise the union would resurrect every id that main.py
had deliberately expired, from the previous commit's copy.
"""

import json
import subprocess
from datetime import datetime, timedelta, timezone

# Keep in sync with main.py. Short on purpose: observed flickers lasted
# one run (6-8 minutes), and on regular stores a sold-out item dropping
# off the list and returning is the restock signal a long grace would hide.
GRACE_MINUTES = 60


def load_local(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return {}


def load_remote(path):
    try:
        raw = subprocess.check_output(
            ["git", "show", f"origin/main:{path}"], stderr=subprocess.DEVNULL
        ).decode("utf-8-sig")
        return json.loads(raw)
    except Exception:
        return {}


def normalize_entry(entry):
    if isinstance(entry, list):
        return {"seen_ids": entry, "zero_streak": 0, "warned": False, "first_failure_at": None, "prices": {}}
    entry.setdefault("prices", {})
    return entry


def last_seen_of(entry, now_iso):
    """An entry from before the grace period has no last_seen - treat
    all its seen ids as just seen, same as main.py does."""
    if "last_seen" in entry:
        return dict(entry["last_seen"])
    return {pid: now_iso for pid in entry.get("seen_ids", [])}


def merge_last_seen(local_entry, remote_entry, now_iso):
    """Per-id newer timestamp, then expire ids relative to the site's
    latest successful run (not the clock, so a site that's been failing
    for a day doesn't lose its memory while it's down)."""
    merged = last_seen_of(remote_entry, now_iso)
    for pid, ts in last_seen_of(local_entry, now_iso).items():
        if pid not in merged or datetime.fromisoformat(ts) > datetime.fromisoformat(merged[pid]):
            merged[pid] = ts

    successes = [e["last_success"] for e in (local_entry, remote_entry) if e.get("last_success")]
    last_success = max(successes, key=datetime.fromisoformat) if successes else None
    if last_success:
        cutoff = datetime.fromisoformat(last_success) - timedelta(minutes=GRACE_MINUTES)
        merged = {pid: ts for pid, ts in merged.items() if datetime.fromisoformat(ts) >= cutoff}
    return merged, last_success


def merge():
    path = "seen_products.json"
    local = load_local(path)
    remote = load_remote(path)

    merged = dict(local)
    now_iso = datetime.now(timezone.utc).isoformat()

    for site_name, remote_entry in remote.items():
        remote_entry = normalize_entry(remote_entry)
        remote_ids = set(remote_entry.get("seen_ids", []))
        remote_prices = remote_entry.get("prices", {})

        local_entry = merged.get(site_name)
        if local_entry is None:
            merged[site_name] = remote_entry
            continue

        local_entry = normalize_entry(local_entry)
        local_ids = set(local_entry.get("seen_ids", []))
        local_prices = local_entry.get("prices", {})

        merged_last_seen, last_success = merge_last_seen(local_entry, remote_entry, now_iso)
        local_entry["last_seen"] = merged_last_seen
        if last_success:
            local_entry["last_success"] = last_success
        local_entry["seen_ids"] = [pid for pid in local_ids | remote_ids if pid in merged_last_seen]

        merged_prices = dict(remote_prices)
        merged_prices.update(local_prices)
        local_entry["prices"] = merged_prices

        merged_availability = dict(remote_entry.get("availability", {}))
        merged_availability.update(local_entry.get("availability", {}))
        local_entry["availability"] = merged_availability

        merged[site_name] = local_entry

    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)


if __name__ == "__main__":
    merge()
