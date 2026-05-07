"""HTTP wrapper around scrape.py — POST /scrape { url, headless? } -> { text }.

Run on Windows WITHOUT uvicorn's --reload flag. --reload forces
SelectorEventLoop on the worker, which on Windows can't spawn subprocesses,
which breaks Playwright's Chromium launch.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scrape import scrape

app = FastAPI(title="linkedintool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    url: str
    headless: bool = True


class ScrapeResponse(BaseModel):
    text: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(req: ScrapeRequest) -> ScrapeResponse:
    try:
        text = await scrape(req.url, headless=req.headless)
    except FileNotFoundError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"scrape failed: {e}")
    return ScrapeResponse(text=text)
