"""
Merges seen_products.json between the current local state and whatever
is on origin/main, combining (union) the "seen_ids" lists AND the
"prices" dictionaries per site, rather than picking one side entirely.
This prevents a merge conflict from ever accidentally discarding
recently-seen products or recently-recorded prices, which was causing
already-notified items (and already-reported price drops) to reappear
and re-trigger duplicate Telegram alerts.
"""

import json
import subprocess


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


def merge():
    path = "seen_products.json"
    local = load_local(path)
    remote = load_remote(path)

    merged = dict(local)

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

        local_entry["seen_ids"] = list(local_ids | remote_ids)

        merged_prices = dict(remote_prices)
        merged_prices.update(local_prices)
        local_entry["prices"] = merged_prices

        merged[site_name] = local_entry

    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)


if __name__ == "__main__":
    merge()
