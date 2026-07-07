from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    page.goto("https://www.coolshit.co.nz/category/pokemon", timeout=30000)
    page.wait_for_timeout(5000)
    page.screenshot(path="debug_coolshit.png", full_page=False)
    print("Page title:", page.title())
    browser.close()
