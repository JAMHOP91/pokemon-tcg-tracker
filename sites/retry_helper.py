"""
Shared retry helper for Playwright-based scrapers. Wraps a fetch
function that might raise (timeout, transient block, network blip)
and retries it a few times with fresh attempts before giving up.
"""

import time


def with_retries(fetch_fn, site_label, max_attempts=3, retry_delay_seconds=10):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fetch_fn()
        except Exception as e:
            last_error = e
            print(f"  {site_label} attempt {attempt}/{max_attempts} failed: {e}")
            if attempt < max_attempts:
                time.sleep(retry_delay_seconds)
    raise last_error
