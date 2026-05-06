# linkedintool

Minimal LinkedIn profile scraper. Loads a saved authenticated session, navigates to a profile URL, scrolls to trigger lazy-loaded sections, and prints the visible profile text to the terminal.

Built with Playwright. No selector-level extraction — LinkedIn rotates CSS class names frequently, so this dumps raw visible text from `<main>` and leaves post-processing to the caller.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate      # macOS / Linux
pip install playwright
playwright install chromium
```

## Create a session

The session file holds your authenticated cookies so the scraper doesn't log in every run.

```powershell
python create_session.py
```

A browser opens. Log in to LinkedIn (handle 2FA / CAPTCHA in the visible window). The script saves cookies to `linkedin_session.json` once login is detected.

> **Security:** `linkedin_session.json` is a credential. It is gitignored and must never be committed.

## Scrape a profile

```powershell
python scrape.py                                       # default: Bill Gates
python scrape.py "https://www.linkedin.com/in/<user>/"
```

Output is the unstructured visible text of the profile's `<main>` element.

## Notes

- LinkedIn's terms of service prohibit scraping. Use a throwaway account, scrape conservatively, and only for data you have a legitimate need for.
- Tested on Python 3.12, Playwright 1.59, Windows 10.
