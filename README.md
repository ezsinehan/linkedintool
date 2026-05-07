# linkedintool

Desktop app for scraping LinkedIn profile data. Tauri (Rust shell) + React frontend talking to a Python (Playwright) backend over local HTTP. The backend will eventually be rewritten in Rust; the HTTP contract is the migration boundary.

## Architecture

```
┌────────────────────┐   POST /scrape    ┌──────────────────┐
│  Tauri WebView     │  ───────────────▶ │  FastAPI         │
│  (React + CSS Mod) │  ◀─────────────── │  + Playwright    │
└────────────────────┘   { text }        └──────────────────┘
        desktop/                                backend/
```

## One-time setup

### Backend (Python)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
playwright install chromium
```

Create a session (visible browser opens, you log in once, cookies are saved):

```powershell
cd backend
python create_session.py
cd ..
```

> `backend\linkedin_session.json` is a credential. It is gitignored.

### Frontend (Tauri)

```powershell
cd desktop
npm install
cd ..
```

First `npm run tauri dev` will compile the Rust shell — expect 5–15 minutes the first time, fast after.

## Run (two terminals)

**Terminal 1 — backend:**

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn api:app --host 127.0.0.1 --port 8000
```

Backend listens on `http://localhost:8000`. Verify with `Invoke-RestMethod http://localhost:8000/health`.

> **Note on `--reload`:** uvicorn's `--reload` flag forces `SelectorEventLoop` on the worker, which on Windows cannot spawn subprocesses — Playwright would fail with `NotImplementedError` when launching Chromium. Don't use `--reload` on Windows with this stack. Restart uvicorn manually after backend changes.

**Terminal 2 — desktop app:**

```powershell
cd desktop
npm run tauri dev
```

A native window opens. Paste a profile URL, click **Scrape**, then **copy** to put the output on your clipboard.

## CLI fallback

The scraper still runs standalone:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python scrape.py "https://www.linkedin.com/in/<user>/"
```

## Notes

- LinkedIn's terms of service prohibit scraping. Use a throwaway account, scrape conservatively, only for data you have a legitimate need for.
- Tested on Python 3.12, Node 22, Rust 1.89, Tauri 2, Windows 10.
