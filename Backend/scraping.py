import sys
import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Playwright, Browser

# Global singleton for Playwright and browser to avoid launching per request
_playwright_instance: Playwright | None = None
_browser_instance: Browser | None = None

async def _initialize_browser():
    global _playwright_instance, _browser_instance
    _playwright_instance = await async_playwright().start()
    _browser_instance = await _playwright_instance.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    )

async def get_browser() -> Browser:
    global _browser_instance
    if _browser_instance is None:
        await _initialize_browser()
    return _browser_instance

async def shutdown():
    global _playwright_instance, _browser_instance
    if _browser_instance:
        await _browser_instance.close()
        _browser_instance = None
    if _playwright_instance:
        await _playwright_instance.stop()
        _playwright_instance = None


MAX_PAGES = 15

# MAIN CRAWLER
async def process_single_page(url, browser, domain):
    page = None
    try:
        page = await browser.new_page()
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font", "stylesheet"] else route.continue_())
        await page.goto(url, wait_until="domcontentloaded")

        # Scrolling to avoid lazy loading
        await page.evaluate("""
async () => {
    await new Promise((resolve) => {
        let totalHeight = 0;
        let distance = 500;
        let timer = setInterval(() => {
            let scrollHeight = document.body.scrollHeight;
            window.scrollBy(0, distance);
            totalHeight += distance;
            if(totalHeight >= scrollHeight){
                clearInterval(timer);
                resolve();
            }
        }, 500);
    });
}
""")

        clean_text = await page.evaluate("""
() => {
    document.querySelectorAll("script, style, noscript").forEach(el => el.remove());
    return document.body.innerText;
}
""")
        if not clean_text:
            await page.close()
            return None, []

        anti_bot_keywords = [
            "Performing security verification",
            "protect against malicious bots",
            "Access Denied",
            "You don't have permission to access",
            "verify you are human",
            "Please enable JS and disable any ad blocker",
            "Checking your browser before accessing",
            "Just a moment...",
            "Reference #"
        ]

        if any(keyword.lower() in clean_text.lower() for keyword in anti_bot_keywords):
            print(f"\n[!] Access Denied: {url}")
            print("[!] This website is blocking web scraping (Bot Protection / WAF detected).")
            await page.close()
            return None, []

        title = await page.title()
        document = {
            "url": url,
            "title": title,
            "content": clean_text
        }

        links = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")
        valid_links = []
        for link in links:
            if not link:
                continue
            parsed = urlparse(link)
            if not parsed.netloc.endswith(domain):
                continue
            clean_link = link.split("#")[0]
            skip_extensions = (".jpg", ".jpeg", ".png", ".gif", ".pdf", ".zip", ".mp4", ".mp3", ".svg", ".webp")
            if clean_link.endswith(skip_extensions):
                continue
            valid_links.append(clean_link)

        await page.close()
        return document, valid_links

    except Exception as e:
        print(f"ERROR crawling {url}: {e}")
        if page:
            try:
                await page.close()
            except:
                pass
        return None, []


async def crawl_website(start_url):
    domain = urlparse(start_url).netloc
    queue = [start_url]
    visited_urls = set()
    all_documents = []
    MAX_CONCURRENT = 2

    browser = await get_browser()

    while queue and len(visited_urls) < MAX_PAGES:
        batch_urls = []
        while queue and len(batch_urls) < MAX_CONCURRENT and (len(visited_urls) + len(batch_urls)) < MAX_PAGES:
            current_url = queue.pop(0)
            if current_url not in visited_urls:
                visited_urls.add(current_url)
                batch_urls.append(current_url)

        if not batch_urls:
            continue

        print(f"\n==============================")
        print(f"Crawling Batch ({len(batch_urls)} pages):")
        for u in batch_urls:
            print(f" - {u}")
        print(f"==============================")

        tasks = [process_single_page(url, browser, domain) for url in batch_urls]
        results = await asyncio.gather(*tasks)

        for doc, new_links in results:
            if doc:
                all_documents.append(doc)
                print(f"SUCCESS: Extracted text from {doc['url']}")
            for link in new_links:
                if link not in visited_urls and link not in queue:
                    queue.append(link)

    return all_documents


async def main():
    url = input("Enter Website URL: ")
    try:
        results = await crawl_website(url)
        print("\n==============================")
        print("TOTAL PAGES SCRAPED:", len(results))
        total_length = sum(len(doc['content']) for doc in results)
        print(f"TOTAL CHARACTERS EXTRACTED: {total_length}")
        print("==============================")
        return results
    finally:
        await shutdown()

if __name__ == "__main__":
    if sys.platform == "win32":
        # Playwright needs ProactorEventLoop for subprocess support on Windows
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(main())
        finally:
            loop.run_until_complete(asyncio.sleep(0.25))  # allow pending callbacks to drain
            loop.close()
    else:
        asyncio.run(main())