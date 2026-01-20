"""Session management routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import os
from orchestrator.lifecycle import Lifecycle

router = APIRouter()

# Initialize lifecycle manager
lifecycle = Lifecycle(
    storage_path="./storage",
    runtime_path="./sandbox_runtime",
    e2b_api_key=os.getenv("E2B_API_KEY")
)


class SessionCreateRequest(BaseModel):
    agent_config: dict = {"type": "code_executor"}
    environment: str = "Python3"
    provider: Literal["docker", "e2b"] = "e2b"


@router.post("/")
def create_session(request: SessionCreateRequest):
    """Create a new session with specified provider.
    
    Args:
        request: Session creation parameters
        
    Returns:
        Session info with sandbox_id and provider
    """
    try:
        session_info = lifecycle.start(
            agent_config=request.agent_config,
            environment=request.environment,
            provider=request.provider
        )
        return session_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
def delete_session(session_id: str, sandbox_id: str):
    """Delete a session and its sandbox.
    
    Args:
        session_id: Session identifier
        sandbox_id: Sandbox/container identifier
        
    Returns:
        Status message
    """
    try:
        success = lifecycle.stop(session_id, sandbox_id)
        if success:
            return {"status": "deleted", "session_id": session_id}
        raise HTTPException(status_code=500, detail="Failed to delete session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
def get_session(session_id: str):
    """Get session state.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session state and metadata
    """
    try:
        state = lifecycle.state_mgr.read_state(session_id)
        provider = lifecycle.sandbox_mgr.get_provider(session_id)
        return {
            "session_id": session_id,
            "provider": provider,
            "state": state,
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Session not found: {str(e)}")
