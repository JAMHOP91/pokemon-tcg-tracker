# Pokemon TCG Restock Tracker (New Zealand)

A free, self-hosted tool that watches New Zealand retailers for new
Pokemon TCG stock (booster boxes, ETBs, tins, blisters, etc.) and sends
instant Telegram alerts when something new appears - filtered to just
cards, no merch/accessories.

Built to solve a real problem: Pokemon TCG restocks in NZ sell out fast,
and no single site or alert service reliably covers every retailer.

## What it does

- Checks 10+ NZ retailers on a schedule (JB Hi-Fi, Cool Shit, The Game
  Tree, Otakumart, Card Masters, Hobby Lords, TCG NZ, Cardtopia,
  WP Games, Collect All Day)
- Filters out non-card merch (mugs, plush, binders, apparel, etc.)
- Shows price and stock status where the retailer's site exposes it
- Sends Telegram notifications the moment something new shows up
- Runs entirely for free via GitHub Actions - no server, no paid API,
  no subscription
- Detects when a site's layout changes and a scraper needs fixing,
  instead of silently going quiet
- Supports "priority keywords" for sets/products you're specifically
  hunting, which get a louder, separate alert
- Supports "hype windows" - date ranges around known set releases where
  checks run every few minutes instead of every 30

## How it works

- Each retailer has its own small Python file in `sites/` that knows how
  to fetch that store's current product listing (either via a public
  JSON feed, or by loading the page with Playwright)
- `main.py` runs every configured site, compares results against what it
  saw last time, and sends alerts on anything new
- `notify.py` handles sending messages via the Telegram Bot API
- GitHub Actions runs the whole thing on a schedule and commits the
  updated "seen" state back to the repo each time
- An external free scheduler (cron-job.org) triggers the GitHub Actions
  workflows reliably, since GitHub's own free scheduled triggers can be
  delayed under load

## Setup

This was built iteratively for one person's specific use case (NZ,
Telegram, a specific set of retailers), so it's not a polished
plug-and-play product - but the pieces are all readable and adaptable:

1. Fork or clone this repo
2. Create a Telegram bot via @BotFather, get your bot token and chat ID
3. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as GitHub repo secrets
   (Settings -> Secrets and variables -> Actions)
4. Adjust or add site files in `sites/` for the retailers you care about
5. Adjust `main.py`'s `SITES` list to match
6. (Optional) set up a free cron-job.org account to trigger the
   workflows reliably instead of relying on GitHub's own scheduler

## Disclaimer

This is a personal hobby project, provided as-is with no warranty.
It scrapes publicly available product listing pages respectfully (no
login bypassing, no automated purchasing, no circumventing anti-bot
protections - sites that actively block automated access are
intentionally excluded rather than worked around). If you adapt this
for your own use, please scrape responsibly and respect each site's
terms of service.
