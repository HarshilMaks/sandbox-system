"""High-level orchestration flow for sandbox lifecycle."""
from .session_manager import SessionManager
from .sandbox_manager import SandboxManager
from .state_manager import StateManager


class Lifecycle:
    """Orchestrates sandbox system lifecycle: create, start, stop, destroy.
    
    This manages the execution environment only. Agent logic lives elsewhere.
    """
    
    def __init__(self, storage_path: str, runtime_path: str):
        self.session_mgr = SessionManager(storage_path)
        self.sandbox_mgr = SandboxManager()
        self.state_mgr = StateManager(runtime_path)
    
    def start(self, agent_config: dict, environment: str) -> dict:
        """Start a new agent session with sandbox."""
        session_id = self.session_mgr.create_session(agent_config)
        container_id = self.sandbox_mgr.start_sandbox(session_id, environment)
        
        return {
            "session_id": session_id,
            "container_id": container_id,
            "status": "running"
        }
    
    def stop(self, session_id: str, container_id: str) -> bool:
        """Stop a session and its sandbox."""
        self.sandbox_mgr.stop_sandbox(container_id)
        self.session_mgr.destroy_session(session_id)
        return True
