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
    """Verify bearer token based on DEVON_API_KEY configuration.

    - Unset/empty: returns 503 telling the operator to configure the key.
    - "disable": allows all requests (explicit opt-out for local dev).
    - Any other value: requires a matching Bearer token.
    """
    expected = os.environ.get("DEVON_API_KEY", "")

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "API key not configured. Set DEVON_API_KEY to a secret value, "
                "or set DEVON_API_KEY=disable to allow unauthenticated access."
            ),
        )

    if expected == "disable":
        return

    if credentials is None or credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
