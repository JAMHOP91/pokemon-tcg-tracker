from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    page.goto("https://www.hobbylords.co.nz/shop/brand/pokemon", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    links = page.query_selector_all('a[href*="/products/single/"]')
    print(f"Links found: {len(links)}")
    for link in links[:5]:
        h4 = link.query_selector("h4")
        print("href:", link.get_attribute("href"))
        print("h4 found:", h4 is not None)
        if h4:
            print("title text:", repr(h4.inner_text()))
        print("---")
    browser.close()
