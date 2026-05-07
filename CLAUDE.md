# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Monorepo with two halves connected by HTTP:

```
backend/  (Python 3.12 + Playwright + FastAPI)  ──HTTP──>  desktop/  (Tauri 2 + React 19 + Vite + plain CSS modules)
```

The HTTP/JSON contract between `backend/api.py` and `desktop/src/App.tsx` is intentionally the **language boundary**: the Python backend is a placeholder for a future Rust implementation. When migrating to Rust, the React frontend should not need to change. Preserve the existing endpoint shapes (`POST /scrape { url, headless } -> { text }`, `GET /health`).

The scraper itself is deliberately minimal: `scrape()` in `backend/scrape.py` does `page.locator("main").inner_text()` and returns the raw text. **Do not add field-level CSS selectors** (`.profile-name`, `[data-test=experience]`, etc.) to extract structured fields — LinkedIn rotates class names specifically to break that pattern. Structured extraction belongs in caller-side post-processing of the text dump, not inside `scrape()`.

`backend/linkedin_session.json` is a credential file (LinkedIn auth cookies). It is gitignored and must never be committed. A burner LinkedIn account is in use; sessions live ~weeks before expiring.

## Common commands

All commands run from the repo root unless noted.

### One-time setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
playwright install chromium
cd desktop ; npm install ; cd ..
```

Then create a session (visible browser opens, log in once):
```powershell
cd backend ; python create_session.py ; cd ..
```

### Running

Two terminals:

```powershell
# Terminal 1 — backend
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn api:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2 — desktop
cd desktop
npm run tauri dev
```

### CLI fallback (no UI)

```powershell
cd backend
python scrape.py "https://www.linkedin.com/in/<user>/"
```

### Health check

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Windows gotcha: never use `uvicorn --reload`

`uvicorn --reload` forces `SelectorEventLoop` on the worker process. On Windows, `SelectorEventLoop` cannot spawn subprocesses, which breaks Playwright's Chromium launch with `NotImplementedError` from `asyncio.create_subprocess_exec`. Symptom: every `POST /scrape` returns 500 with an empty error message.

**Run uvicorn without `--reload` on Windows.** Restart manually after backend changes. This is documented in `backend/api.py`'s module docstring and the README — do not add `--reload` back.

## Frontend conventions

- **Plain CSS modules** (`*.module.css`), no Tailwind, no component library. Set deliberately by the user for styling practice.
- **Lowercase UI labels** everywhere — buttons (`scrape`, `copy`), section headers (`output`), toggle text. The only place text is presented in mixed/upper case is the actual scraped output.
- **Square corners** — no `border-radius` anywhere. Aesthetic choice; preserve it when adding new UI.
- The header is just `linkedintool`; no subtitle.
- Headless toggle in the UI: the checkbox controls the `headless` flag passed to `POST /scrape`. Off = visible Chromium pops up alongside the Tauri window during scraping.

## Backend changes require manual restart

Vite hot-reloads `desktop/` automatically while `npm run tauri dev` is running. The backend has no reloader (because of the `--reload` issue above), so any change to `backend/*.py` requires killing and restarting uvicorn.
