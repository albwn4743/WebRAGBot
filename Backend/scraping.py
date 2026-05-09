import asyncio
from urllib.parse import urlparse

from playwright.async_api import async_playwright
import trafilatura


MAX_PAGES = 20
visited_urls = set()
# MAIN CRAWLER
async def process_single_page(url, browser, domain):
    page = None
    try:
        page = await browser.new_page()
        
        # Block unnecessary resources to drastically speed up loading
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font", "stylesheet"] else route.continue_())
        
        # Use domcontentloaded instead of networkidle
        await page.goto(url, wait_until="domcontentloaded")
        
        # Fast scroll to trigger lazy loading (1000px every 100ms)
        await page.evaluate("""
async () => {
    await new Promise((resolve) => {
        let totalHeight = 0;
        let distance = 1000;
        let timer = setInterval(() => {
            let scrollHeight = document.body.scrollHeight;
            window.scrollBy(0, distance);
            totalHeight += distance;
            if(totalHeight >= scrollHeight){
                clearInterval(timer);
                resolve();
            }
        }, 100);
    });
}
""")
        
        # Clean content
        clean_text = await page.evaluate("""
() => {
    document.querySelectorAll("script, style, noscript").forEach(el => el.remove());
    return document.body.innerText;
}
""")
        if not clean_text:
            await page.close()
            return None, []
            
        title = await page.title()
        document = {
            "url": url,
            "title": title,
            "content": clean_text
        }
        
        # Extract links
        links = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")
        
        # Filter links
        valid_links = []
        for link in links:
            if not link:
                continue
            parsed = urlparse(link)
            if parsed.netloc != domain:
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
    all_documents = []
    MAX_CONCURRENT = 5 # Number of tabs to open at once

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        while queue and len(visited_urls) < MAX_PAGES:
            batch_urls = []
            
            # Pull up to MAX_CONCURRENT URLs from the queue
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

            # Process the batch concurrently
            tasks = [process_single_page(url, browser, domain) for url in batch_urls]
            results = await asyncio.gather(*tasks)

            # Collect results and add new links to queue
            for doc, new_links in results:
                if doc:
                    all_documents.append(doc)
                    print(f"SUCCESS: Extracted text from {doc['url']}")
                
                for link in new_links:
                    if link not in visited_urls and link not in queue:
                        queue.append(link)

        await browser.close()

    return all_documents


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    url = input("Enter Website URL: ")

    results = asyncio.run(crawl_website(url))

    print("\n==============================")
    print("TOTAL PAGES SCRAPED:", len(results))
    
    total_length = sum(len(doc['content']) for doc in results)
    print(f"TOTAL CHARACTERS EXTRACTED: {total_length}")
    print("==============================")