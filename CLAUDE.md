# Pokemon TCG NZ restock tracker
Python scrapers for NZ retailers, run by GitHub Actions (triggered from cron-job.org). Alerts go to Telegram, and the dashboard is index.html on GitHub Pages.

## Rules
- Do NOT open these files. The bot writes them and they are huge: seen_products.json, release_history.json, status.json, *_state.json.
- Never hand-edit them. On a git conflict in them: git checkout --theirs <file>, git add, commit.
- main.py must contain exactly one `def main`. Check: Select-String -Path main.py -Pattern "^def main"
- Before every commit, run all four checks and do not commit if any fails:
  - `py -m py_compile main.py notify.py msrp.py test_msrp.py (Get-ChildItem sites\*.py).FullName`
  - `(Select-String -Path main.py -Pattern "^def main").Count -eq 1` must print True
  - `py test_filters.py` must exit 0 (filter regression test)
  - `py test_msrp.py` must exit 0 (MSRP type matching and FX fallback test, no network)
- Sites live in sites/. Shopify stores use sites/shopify_helper.py, Playwright sites use sites/retry_helper.py, and product filtering is in sites/filters.py.
- Do not run main.py with real Telegram credentials unless asked. It sends real alerts.
- hype_windows.json uses UTC dates, so pad start dates by a day.
- Windows and PowerShell.
- Use py, not python; python isn't installed.
