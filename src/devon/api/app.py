"""FastAPI application factory for DEVON."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from devon.config.settings import Settings
from devon.storage.organizer import ModelStorage

# Ensure source plugins are registered
import devon.sources  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Initialize shared resources once at startup."""
    # Resolve paths — env vars override defaults for container use
    config_path = os.environ.get("DEVON_CONFIG_PATH")
    storage_path = os.environ.get("DEVON_STORAGE_PATH")

    settings = Settings(config_path=Path(config_path) if config_path else None)

    if storage_path:
        base_path = Path(storage_path)
    else:
        base_path = settings.storage_path

    storage = ModelStorage(base_path=base_path)

    app.state.settings = settings
    app.state.storage = storage

    yield


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    app = FastAPI(
        title="DEVON API",
        description="REST API for DEVON — model discovery and management",
        version="1.0.0",
        lifespan=lifespan,
    )

    # -- CORS middleware --
    from starlette.middleware.cors import CORSMiddleware

    allowed_origins = os.environ.get("DEVON_CORS_ORIGINS", "").split(",")
    allowed_origins = [o.strip() for o in allowed_origins if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins or ["http://localhost:*"],
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )

    # -- Security headers middleware --
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if os.environ.get("DEVON_ENABLE_HSTS"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Import routers here to avoid circular imports
    from devon.api.routers.health import router as health_router
    from devon.api.routers.models import router as models_router
    from devon.api.routers.search import router as search_router
    from devon.api.routers.download import router as download_router
    from devon.api.routers.storage import router as storage_router

    app.include_router(health_router)
    app.include_router(models_router)
    app.include_router(search_router)
    app.include_router(download_router)
    app.include_router(storage_router)

    return app
