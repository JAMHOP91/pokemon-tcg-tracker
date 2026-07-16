"""
Sends messages to your Telegram chat via a bot.
"""

import os
import requests

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables.")

    url = TELEGRAM_API_URL.format(token=token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()


def notify_new_products(site_name: str, products: list[dict]) -> None:
    if not products:
        return

    CHUNK_SIZE = 20
    for i in range(0, len(products), CHUNK_SIZE):
        chunk = products[i:i + CHUNK_SIZE]
        chunk_number = i // CHUNK_SIZE + 1
        total_chunks = (len(products) + CHUNK_SIZE - 1) // CHUNK_SIZE

        header = f"NEW: {len(products)} new item(s) on {site_name}"
        if total_chunks > 1:
            header += f" (part {chunk_number}/{total_chunks})"

        lines = [header]
        for p in chunk:
            price = f" - {p['price']}" if p.get("price") else ""
            lines.append(f"- <a href=\"{p['url']}\">{p['title']}</a>{price}")

        send_telegram_message("\n".join(lines))


def notify_scraper_warning(site_name: str, elapsed_minutes: int) -> None:
    hours = elapsed_minutes // 60
    minutes = elapsed_minutes % 60
    duration = f"{hours}h {minutes}m" if hours else f"{minutes} min"
    text = (
        f"WARNING: {site_name} has been failing continuously for {duration}. "
        f"This usually means the site changed its layout and the scraper needs fixing, "
        f"not that the store is actually empty."
    )
    send_telegram_message(text)


def notify_scraper_recovered(site_name: str) -> None:
    send_telegram_message(f"RESOLVED: {site_name} is working again.")


def notify_priority_products(site_name: str, products: list[dict]) -> None:
    if not products:
        return

    lines = [f"PRIORITY DROP on {site_name}!"]
    for p in products:
        price = f" - {p['price']}" if p.get("price") else ""
        lines.append(f"- <a href=\"{p['url']}\">{p['title']}</a>{price}")

    send_telegram_message("\n".join(lines))
