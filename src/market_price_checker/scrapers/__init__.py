import asyncio
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, BrowserContext

# Helper to clean price string
def parse_price(price_str: str) -> int:
    import re
    if not price_str:
        return 0
    # Remove non-digits
    nums = re.sub(r'[^\d]', '', price_str)
    try:
        return int(nums)
    except ValueError:
        return 0

async def search_amazon(context: BrowserContext, keyword: str) -> List[Dict]:
    results = []
    page = await context.new_page()
    try:
        # Amazon requires avoiding bot detection.
        # In a real scenario, we might need stealth plugins or human-like behavior.
        await page.goto(f"https://www.amazon.co.jp/s?k={keyword}", timeout=30000)

        # Select items
        items = await page.locator("div[data-component-type='s-search-result']").all()

        for item in items[:5]: # Limit to top 5
            try:
                title_el = item.locator("h2 span")
                price_el = item.locator(".a-price-whole")
                link_el = item.locator("h2 a")

                if await title_el.count() > 0 and await price_el.count() > 0:
                    title = await title_el.first.inner_text()
                    price_text = await price_el.first.inner_text()
                    url_suffix = await link_el.get_attribute("href")
                    url = f"https://www.amazon.co.jp{url_suffix}" if url_suffix else ""

                    results.append({
                        "site": "Amazon",
                        "title": title,
                        "price": parse_price(price_text),
                        "url": url
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"Amazon error: {e}")
        # Return empty list on failure
    finally:
        await page.close()
    return results

async def search_yahoo(context: BrowserContext, keyword: str) -> List[Dict]:
    results = []
    page = await context.new_page()
    try:
        await page.goto(f"https://shopping.yahoo.co.jp/search?p={keyword}", timeout=30000)

        # Yahoo structure (approximate)
        items = await page.locator(".LoopList__item").all()
        if not items:
             # Fallback for list view or other layouts
             items = await page.locator("li.LoopList__item").all()

        for item in items[:5]:
            try:
                title_el = item.locator("a[data-cl-params*='title']") # rough selector
                if await title_el.count() == 0:
                     title_el = item.locator(".LoopList__itemTitle")

                price_el = item.locator(".LoopList__itemPrice")

                if await title_el.count() > 0 and await price_el.count() > 0:
                    title = await title_el.first.inner_text()
                    price_text = await price_el.first.inner_text()
                    url = await title_el.first.get_attribute("href")

                    results.append({
                        "site": "Yahoo",
                        "title": title,
                        "price": parse_price(price_text),
                        "url": url
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"Yahoo error: {e}")
    finally:
        await page.close()
    return results

async def search_rakuten(context: BrowserContext, keyword: str) -> List[Dict]:
    results = []
    page = await context.new_page()
    try:
        # Rakuten search URL
        await page.goto(f"https://search.rakuten.co.jp/search/mall/{keyword}/", timeout=30000)

        items = await page.locator(".searchresultitem").all()

        for item in items[:5]:
            try:
                title_el = item.locator(".title a")
                price_el = item.locator(".price .important") # often has price

                if await title_el.count() > 0:
                    title = await title_el.first.inner_text()
                    if await price_el.count() > 0:
                        price_text = await price_el.first.inner_text()
                    else:
                        price_text = "0"

                    url = await title_el.first.get_attribute("href")

                    results.append({
                        "site": "Rakuten",
                        "title": title,
                        "price": parse_price(price_text),
                        "url": url
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"Rakuten error: {e}")
    finally:
        await page.close()
    return results

async def search_bic(context: BrowserContext, keyword: str) -> List[Dict]:
    results = []
    page = await context.new_page()
    try:
        await page.goto(f"https://www.biccamera.com/bc/main/", timeout=30000)
        # Type in search box and submit
        await page.fill("#txt_search_kwd", keyword)
        await page.click("#btn_search")
        await page.wait_for_load_state("domcontentloaded")

        items = await page.locator(".prod_box").all()

        for item in items[:5]:
            try:
                title_el = item.locator(".bcs_item")
                price_el = item.locator(".bcs_price")

                if await title_el.count() > 0 and await price_el.count() > 0:
                    title = await title_el.first.inner_text()
                    price_text = await price_el.first.inner_text()
                    # Link is usually on the title or image
                    link_el = item.locator(".bcs_item a")
                    url_suffix = await link_el.first.get_attribute("href")
                    url = f"https://www.biccamera.com{url_suffix}" if url_suffix else ""

                    results.append({
                        "site": "BicCamera",
                        "title": title,
                        "price": parse_price(price_text),
                        "url": url
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"Bic error: {e}")
    finally:
        await page.close()
    return results

async def search_all(keyword: str) -> List[Dict]:
    async with async_playwright() as p:
        # Launch browser once
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Run all scrapers in parallel
        # Note: We must pass the context or use a new context for each if we want true parallelism without cookies/session sharing issues,
        # but sharing a context is faster. For different sites it is fine.
        results = await asyncio.gather(
            search_amazon(context, keyword),
            search_yahoo(context, keyword),
            search_rakuten(context, keyword),
            search_bic(context, keyword)
        )

        await context.close()
        await browser.close()

    # Flatten the list of lists
    flat_results = []
    for r in results:
        flat_results.extend(r)

    # Sort by price
    flat_results.sort(key=lambda x: x['price'])

    return flat_results
