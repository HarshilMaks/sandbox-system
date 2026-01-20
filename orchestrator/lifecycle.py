"""High-level orchestration flow for sandbox lifecycle."""
from typing import Optional
from .session_manager import SessionManager
from .unified_manager import UnifiedSandboxManager
from .state_manager import StateManager


class Lifecycle:
    """Orchestrates sandbox system lifecycle: create, start, stop, destroy.
    
    This manages the execution environment only. Agent logic lives elsewhere.
    Supports both Docker and E2B providers.
    """
    
    def __init__(self, storage_path: str, runtime_path: str, e2b_api_key: Optional[str] = None):
        self.session_mgr = SessionManager(storage_path)
        self.sandbox_mgr = UnifiedSandboxManager(e2b_api_key=e2b_api_key)
        self.state_mgr = StateManager(runtime_path)
    
    def start(self, agent_config: dict, environment: str, provider: str = "docker") -> dict:
        """Start a new agent session with sandbox.
        
        Args:
            agent_config: Agent configuration
            environment: Environment name or template
            provider: "docker" or "e2b"
            
        Returns:
            Session info with sandbox_id, provider, and status
        """
        session_id = self.session_mgr.create_session(agent_config)
        
        sandbox_info = self.sandbox_mgr.start_sandbox(
            session_id=session_id,
            environment=environment,
            provider=provider
        )
        
        return {
            "session_id": session_id,
            "sandbox_id": sandbox_info["sandbox_id"],
            "provider": sandbox_info["provider"],
            "status": "running",
            "url": sandbox_info.get("url")
        }
    
    def stop(self, session_id: str, sandbox_id: str) -> bool:
        """Stop a session and its sandbox."""
        self.sandbox_mgr.stop_sandbox(session_id, sandbox_id)
        self.session_mgr.destroy_session(session_id)
        return True
