from contextlib import asynccontextmanager
from importlib import import_module
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings
from .database import init_db

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"


def _load_seed_all():
    try:
        return import_module("seed.seed_all").seed_all
    except ModuleNotFoundError as error:
        if error.name != "seed":
            raise
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Auto-seed on first startup (safe to call - skips if data exists)
    try:
        seed_all = _load_seed_all()
        if seed_all is not None:
            await seed_all()
    except Exception as e:
        print(f"[Seed] Skipping auto-seed: {e}")

    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS: only needed in dev mode when frontend runs on separate port.
# In production, frontend is served from same origin.
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- API routes ---
from .api import knowledge, questions, practice, ai, review, exam, documents, progress

app.include_router(knowledge.router)
app.include_router(questions.router)
app.include_router(practice.router)
app.include_router(ai.router)
app.include_router(review.router)
app.include_router(exam.router)
app.include_router(documents.router)
app.include_router(progress.router)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "mode": settings.APP_MODE,
        "user_label": settings.APP_USER_LABEL,
    }


# --- SPA fallback: serve frontend static files in production ---
if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
    # Mount static assets at /assets
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="spa_assets")

    # Also serve files in public/ at root
    for pub_file in FRONTEND_DIR.glob("*"):
        if pub_file.is_file() and pub_file.name != "index.html":
            pass  # handled below

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str = ""):
        """Serve frontend SPA: return index.html for all non-API routes."""
        file_path = FRONTEND_DIR / full_path
        # If request is for a real file (not a directory), serve it
        if file_path.is_file():
            return FileResponse(str(file_path))

        # Otherwise fall back to index.html (SPA routing)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))

        return {"message": "Frontend not built. Run: cd frontend && npm run build"}
