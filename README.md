# Pokemon TCG Product Tracker

Checks a list of websites on a schedule, and sends you a Telegram message
whenever a new product shows up.

## How it works

- `main.py` loops through the sites registered in `SITES`
- Each site module exposes `get_current_products()`, returning a list of
  `{"id", "title", "url", "price"}` dicts
- `main.py` compares the current list against `seen_products.json`
  (what was seen last run) and notifies on anything new
- `notify.py` sends the alert to your Telegram chat
- GitHub Actions runs this on a schedule so you don't need your PC on

---

## Step 1 — Create your Telegram bot

1. Open Telegram, search for **@BotFather**, and start a chat.
2. Send `/newbot` and follow the prompts (pick a name and a username).
3. BotFather will give you a **bot token** — looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`. Save it.
4. Start a chat with your new bot (search its username, hit Start) and send it any message — this lets it message you back.
5. Get your **chat ID**:
   - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser (replace `<YOUR_TOKEN>`)
   - Send your bot another message, refresh the page
   - Look for `"chat":{"id":123456789, ...}` in the JSON — that number is your chat ID

You now have `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

---

## Step 2 — Test locally (optional but recommended)

```bash
cd pokemon-tcg-tracker
pip install -r requirements.txt
playwright install chromium

export TELEGRAM_BOT_TOKEN="your-token-here"
export TELEGRAM_CHAT_ID="your-chat-id-here"

python main.py
```

You should see console output for each site being checked. The first run will
report everything as "new" (since `seen_products.json` starts empty) — that's
expected. Run it a second time and it should report no new products.

---

## Step 3 — Customize the site scrapers

This starter includes two templates:

- **`sites/example_shopify_site.py`** — for small/hobby TCG shops running on
  Shopify. Just change `BASE_URL` to the real store domain. Many Shopify
  stores expose `/products.json` for free, no scraping needed.
- **`sites/example_playwright_site.py`** — for big retailers with
  JavaScript-rendered pages. You'll need to:
  1. Open the real product listing page in your browser
  2. Right-click a product card → Inspect
  3. Find the CSS selectors for the product card, title, link, and price
  4. Update the `*_SELECTOR` constants at the top of the file

For each new site you want to track:
1. Copy whichever template fits (Shopify vs. big-retailer)
2. Rename the file (e.g. `sites/target.py`)
3. Fill in the URL and selectors
4. Register it in `main.py`'s `SITES` list:
   ```python
   from sites import target
   SITES = [
       (example_shopify_site.SITE_NAME, example_shopify_site),
       (target.SITE_NAME, target),
   ]
   ```

**Tip:** start with 2–3 sites, confirm they work, then add more. Big retailer
selectors are the most likely thing to break over time and need occasional
maintenance.

---

## Step 4 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial tracker setup"
git branch -M main
git remote add origin https://github.com/<your-username>/pokemon-tcg-tracker.git
git push -u origin main
```

---

## Step 5 — Add your secrets to GitHub

In your GitHub repo:
1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**, add:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

---

## Step 6 — Let it run

The workflow in `.github/workflows/check.yml` runs every 30 minutes
automatically once pushed. You can also trigger it manually:

- Go to the **Actions** tab in your repo → select the workflow → **Run workflow**

Each run commits the updated `seen_products.json` back to the repo, so state
persists between runs without needing a database.

---

## Adjusting the schedule

Edit the `cron` line in `.github/workflows/check.yml`. Examples:

- Every 15 minutes: `*/15 * * * *`
- Every hour: `0 * * * *`
- Every 5 minutes (only if really needed — be considerate of the sites you're checking): `*/5 * * * *`

Note: GitHub Actions scheduled runs aren't perfectly precise and can be
delayed a few minutes during high load — fine for restock alerts, not for
sub-minute precision.

---

## A note on big retailers

Sites like Target/Walmart/Best Buy actively try to detect and block
automated traffic. Keep the check interval reasonable (don't hammer them),
expect selectors to need updates occasionally, and know that some may
require additional handling (rotating user agents, proxies) if you get
blocked — that's outside the scope of this starter, but the Shopify-based
shops should just work.
