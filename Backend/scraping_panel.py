import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from scraping import process_single_page

async def scrape_panel_single_url(url: str):
    """
    Fetch one page and return a document dict compatible with upload_docs:
    {"url", "title", "content"} or None on failure / bot wall.
    """
    domain = urlparse(url).netloc
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            document, _links = await process_single_page(url, browser, domain)
            return document
        finally:
            await browser.close()


def scrape_panel_single_url_sync(url: str):
    """Synchronous helper for FastAPI background tasks."""
    return asyncio.run(scrape_panel_single_url(url))


if __name__ == "__main__":
    u = input("URL: ").strip()
    doc = asyncio.run(scrape_panel_single_url(u))
    if doc:
        print("Title:", doc.get("title"))
        print("Chars:", len(doc.get("content") or ""))
    else:
        print("No document extracted.")
