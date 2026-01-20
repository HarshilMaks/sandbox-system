"""Session management routes."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def create_session(agent_config: dict):
    """Create a new session."""
    # Implementation
    return {"session_id": "example-id", "status": "created"}


@router.delete("/{session_id}")
def delete_session(session_id: str):
    """Delete a session."""
    # Implementation
    return {"status": "deleted"}


@router.get("/{session_id}")
def get_session(session_id: str):
    """Get session info."""
    # Implementation
    return {"session_id": session_id, "status": "active"}
