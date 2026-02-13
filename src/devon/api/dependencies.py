"""Shared FastAPI dependencies for the DEVON API."""

import os
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from devon.config.settings import Settings
from devon.sources.registry import SourceRegistry
from devon.storage.organizer import ModelStorage

# Optional bearer token — only enforced when DEVON_API_KEY is set
_bearer_scheme = HTTPBearer(auto_error=False)


def get_settings(request: Request) -> Settings:
    """Retrieve the Settings instance stored at startup."""
    return request.app.state.settings


def get_storage(request: Request) -> ModelStorage:
    """Retrieve the ModelStorage instance stored at startup."""
    return request.app.state.storage


def get_source(source_name: str = "huggingface"):
    """Instantiate a source plugin by name."""
    try:
        return SourceRegistry.get_source(source_name)()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


async def verify_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)] = None,
) -> None:
    """Verify bearer token if DEVON_API_KEY is configured.

    When the env var is unset or empty, all requests are allowed.
    """
    expected = os.environ.get("DEVON_API_KEY", "")
    if not expected:
        return

    if credentials is None or credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
