"""Sandbox management routes."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/start")
def start_sandbox(session_id: str, environment: str):
    """Start a sandbox container."""
    # Implementation
    return {"container_id": "example-container", "status": "started"}


@router.post("/stop")
def stop_sandbox(container_id: str):
    """Stop a sandbox container."""
    # Implementation
    return {"status": "stopped"}


@router.get("/status/{container_id}")
def get_status(container_id: str):
    """Get sandbox status."""
    # Implementation
    return {"container_id": container_id, "status": "running"}
