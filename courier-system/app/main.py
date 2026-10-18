"""
App entrypoint. Run with:
    uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import pages, auth, packages

app = FastAPI(title="Courier & Logistics Tracking System — Phase 1")

# Signed session cookie — this is how we remember who's logged in between
# requests, for all three roles (Customer, Rider, Admin/Dispatcher).
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(packages.router)


@app.on_event("startup")
def on_startup():
    # Fails fast with a clear message if .env isn't set up, instead of a
    # confusing error on the first database call.
    settings.validate()
