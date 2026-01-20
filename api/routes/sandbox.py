"""Sandbox management routes (DEPRECATED - Use /api/sessions instead)."""
from fastapi import APIRouter, HTTPException
import warnings

router = APIRouter()

warnings.warn(
    "Sandbox routes are deprecated. Use /api/sessions for unified Docker/E2B management.",
    DeprecationWarning
)


@router.post("/start")
def start_sandbox(session_id: str, environment: str):
    """Start a sandbox container (DEPRECATED)."""
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use POST /api/sessions instead."
    )


@router.post("/stop")
def stop_sandbox(container_id: str):
    """Stop a sandbox container (DEPRECATED)."""
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use DELETE /api/sessions/{session_id} instead."
    )


@router.get("/status/{container_id}")
def get_status(container_id: str):
    """Get sandbox status (DEPRECATED)."""
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use GET /api/sessions/{session_id} instead."
    )
