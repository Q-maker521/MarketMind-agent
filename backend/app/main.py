from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings

PROJECT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = PROJECT_DIR / "frontend" / "dist"


def create_app() -> FastAPI:
    app = FastAPI(
        title="MarketMind Agent API",
        version="0.1.0",
        description="Demo API for the MarketMind Agent investment research workflow.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    _mount_frontend(app)

    return app


def _mount_frontend(app: FastAPI) -> None:
    index_file = FRONTEND_DIST_DIR / "index.html"
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if not index_file.exists():
        return

    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str) -> FileResponse:
        requested_file = FRONTEND_DIST_DIR / full_path
        if full_path and requested_file.is_file():
            return FileResponse(requested_file)
        return FileResponse(index_file)


app = create_app()
