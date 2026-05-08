import asyncio
from urllib.parse import urlparse

from playwright.async_api import async_playwright
import trafilatura


MAX_PAGES = 20
visited_urls = set()
# MAIN CRAWLER
async def crawl_website(start_url):
    domain = urlparse(start_url).netloc
    queue = [start_url]
    all_documents = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        while queue and len(visited_urls) < MAX_PAGES:

            current_url = queue.pop(0)

            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)

            print(f"\n==============================")
            print(f"Crawling: {current_url}")
            print(f"==============================")

            try:

                # ==========================================
                # STEP 1: RENDER WEBSITE
                # ==========================================

                await page.goto(
                    current_url,
                    wait_until="networkidle",
                    # timeout=60000
                )

                # wait for JS rendering
                # await page.wait_for_timeout(5000)

                # ==========================================
                # STEP 2: GET FULL RENDERED HTML
                # ==========================================
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
                # ==========================================
                # STEP 3: CLEAN CONTENT USING TRAFILATURA
                # ==========================================

                clean_text = await page.evaluate("""
() => {

    // remove scripts/styles
    document.querySelectorAll("script, style, noscript")
        .forEach(el => el.remove());

    return document.body.innerText;
}
""")
                if not clean_text:
                    print("No readable content found.")
                    continue

                # ==========================================
                # STEP 4: STORE CLEAN CONTENT
                # ==========================================

                document = {
                    "url": current_url,
                    'title': await page.title(),
                    "content": clean_text
                }

                all_documents.append(document)

                print("\n========= CLEAN CONTENT =========\n")

                print(clean_text[:3000])

                print("\n=================================\n")

                # ==========================================
                # STEP 5: EXTRACT INTERNAL LINKS
                # ==========================================

                links = await page.eval_on_selector_all(
                    "a",
                    """
                    elements => elements.map(el => el.href)
                    """
                )

                print(f"Found {len(links)} links")

                # ==========================================
                # STEP 6: RECURSIVE CRAWLING
                # ==========================================

                for link in links:

                    if not link:
                        continue

                    parsed = urlparse(link)

                    # SAME DOMAIN ONLY
                    if parsed.netloc != domain:
                        continue

                    # REMOVE URL FRAGMENTS
                    clean_link = link.split("#")[0]

                    # SKIP DUPLICATES
                    if clean_link in visited_urls:
                        continue

                    # SKIP FILE TYPES
                    skip_extensions = (
                        ".jpg", ".jpeg", ".png", ".gif",
                        ".pdf", ".zip", ".mp4", ".mp3",
                        ".svg", ".webp"
                    )

                    if clean_link.endswith(skip_extensions):
                        continue

                    queue.append(clean_link)

            except Exception as e:

                print(f"ERROR: {e}")

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
    print("==============================")