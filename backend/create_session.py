"""Open a browser, let user log in to LinkedIn manually, save session cookies."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SESSION_FILE = Path(__file__).parent / "linkedin_session.json"


async def main():
    print("Opening browser. Log in to LinkedIn, then return to this terminal.")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.linkedin.com/login")

        try:
            await page.wait_for_url(
                lambda url: "/login" not in url and "/checkpoint" not in url,
                timeout=300_000,
            )
        except Exception:
            print("Timed out waiting for login.")
            await browser.close()
            return

        await context.storage_state(path=str(SESSION_FILE))
        print(f"Session saved to {SESSION_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
