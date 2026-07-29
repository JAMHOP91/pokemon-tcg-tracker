from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    page.goto("https://www.hobbylords.co.nz/shop/brand/pokemon", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    links = page.query_selector_all('a[href*="/products/single/"]')
    link = links[0]
    print("Full inner HTML of first link:")
    print(link.inner_html())
    browser.close()
