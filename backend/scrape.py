"""Minimal LinkedIn profile scraper: load session, dump visible profile text."""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

SESSION_FILE = Path(__file__).parent / "linkedin_session.json"


async def scrape(url: str, headless: bool = True) -> str:
    if not SESSION_FILE.exists():
        raise FileNotFoundError(
            f"No session at {SESSION_FILE}. Run: python create_session.py"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            storage_state=str(SESSION_FILE),
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_selector("main", timeout=15_000)
        await page.wait_for_timeout(2_500)

        for _ in range(6):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(400)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        text = await page.locator("main").inner_text()
        await browser.close()
        return text


def _cli():
    url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://www.linkedin.com/in/williamhgates/"
    )
    print(f"Scraping: {url}\n" + "=" * 60)
    try:
        print(asyncio.run(scrape(url, headless=False)))
    except FileNotFoundError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    _cli()
