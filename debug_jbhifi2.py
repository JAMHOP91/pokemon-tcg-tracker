from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    page.goto("https://www.jbhifi.co.nz/collections/collectibles-merchandise/pokemon-trading-cards", timeout=30000)
    page.wait_for_timeout(5000)
    print("Page title:", page.title())
    print("Page text sample:", page.inner_text("body")[:500])
    browser.close()
