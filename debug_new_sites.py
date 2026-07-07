from playwright.sync_api import sync_playwright

sites_to_check = {
    "tcgnz": "https://www.tcgnz.co.nz/shop-collection",
    "whitcoulls": "https://www.whitcoulls.co.nz/games-puzzles/games/collectible-cards",
    "kmart": "https://www.kmart.co.nz/category/toys/pokemon-trading-cards/",
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, url in sites_to_check.items():
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)
            page.screenshot(path=f"debug_{name}.png", full_page=False)
            print(f"{name}: title = {page.title()}")
        except Exception as e:
            print(f"{name}: FAILED - {e}")
        page.close()
    browser.close()
