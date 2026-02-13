"""Model download endpoint."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from devon.api.dependencies import get_source, get_storage, verify_api_key
from devon.api.schemas import DownloadRequest, DownloadResponse
from devon.storage.organizer import ModelStorage

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.post("/downloads", response_model=DownloadResponse)
async def download_model(
    body: DownloadRequest,
    storage: ModelStorage = Depends(get_storage),
):
    """Download a model. Runs synchronously — set long client timeouts."""
    # Check if already downloaded
    if not body.force and storage.is_downloaded(body.source, body.model_id):
        existing = storage.get_model_entry(body.source, body.model_id)
        if existing is None:
            raise HTTPException(
                status_code=500,
                detail=f"Index inconsistency: {body.source}/{body.model_id} marked as downloaded but entry missing",
            )
        return DownloadResponse(
            model_id=body.model_id,
            source=body.source,
            path=existing["path"],
            files=existing["files"],
            size_bytes=existing["size_bytes"],
        )

    source_impl = get_source(body.source)

    # Fetch remote info
    try:
        model_info = source_impl.get_model_info(body.model_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Model not found: {exc}")

    dest = storage.get_model_path(body.source, body.model_id)

    # Download
    try:
        allow_patterns = body.include_patterns if body.include_patterns else None
        files = source_impl.download_model(body.model_id, str(dest), allow_patterns=allow_patterns)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Download failed: {exc}")

    # Register in index
    metadata_dict = asdict(model_info)
    storage.register_model(
        source=body.source,
        model_id=body.model_id,
        metadata=metadata_dict,
        files=files,
    )

    entry = storage.get_model_entry(body.source, body.model_id)
    if entry is None:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: entry missing after register for {body.source}/{body.model_id}",
        )
    return DownloadResponse(
        model_id=body.model_id,
        source=body.source,
        path=entry["path"],
        files=entry["files"],
        size_bytes=entry["size_bytes"],
    )
