"""Unified sandbox manager supporting Docker and E2B."""
from typing import Literal, Optional
from .sandbox_manager import SandboxManager
from .e2b_manager import E2BSandboxManager


SandboxProvider = Literal["docker", "e2b"]


class UnifiedSandboxManager:
    """Manages sandboxes across multiple providers (Docker, E2B).
    
    Provides a unified interface for creating and managing sandboxes
    regardless of the underlying provider.
    """
    
    def __init__(self, e2b_api_key: Optional[str] = None):
        """Initialize unified manager.
        
        Args:
            e2b_api_key: E2B API key (optional, can use env var)
        """
        self.docker_manager = SandboxManager()
        self.e2b_manager = E2BSandboxManager(api_key=e2b_api_key)
        self.session_providers = {}  # session_id -> provider
    
    def start_sandbox(
        self, 
        session_id: str, 
        environment: str,
        provider: SandboxProvider = "docker"
    ) -> dict:
        """Start a sandbox with specified provider.
        
        Args:
            session_id: Unique session identifier
            environment: Environment config (image name or E2B template)
            provider: "docker" or "e2b"
            
        Returns:
            Dict with sandbox_id, provider, and metadata
        """
        if provider == "docker":
            container_id = self.docker_manager.start_sandbox(session_id, environment)
            self.session_providers[session_id] = "docker"
            return {
                "sandbox_id": container_id,
                "provider": "docker",
                "session_id": session_id
            }
        
        elif provider == "e2b":
            sandbox_id = self.e2b_manager.start_sandbox(session_id, environment)
            self.session_providers[session_id] = "e2b"
            return {
                "sandbox_id": sandbox_id,
                "provider": "e2b",
                "session_id": session_id,
                "url": self.e2b_manager.get_sandbox_url(session_id)
            }
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def stop_sandbox(self, session_id: str, sandbox_id: str) -> bool:
        """Stop a sandbox.
        
        Args:
            session_id: Session identifier
            sandbox_id: Sandbox/container ID
            
        Returns:
            Success status
        """
        provider = self.session_providers.get(session_id)
        
        if provider == "docker":
            return self.docker_manager.stop_sandbox(sandbox_id)
        
        elif provider == "e2b":
            return self.e2b_manager.stop_sandbox(session_id)
        
        return False
    
    def execute_code(self, session_id: str, code: str, language: str = "python") -> dict:
        """Execute code in sandbox (E2B only).
        
        Args:
            session_id: Session identifier
            code: Code to execute
            language: Programming language
            
        Returns:
            Execution result
        """
        provider = self.session_providers.get(session_id)
        
        if provider == "e2b":
            return self.e2b_manager.execute_code(session_id, code, language)
        
        raise NotImplementedError("Code execution only supported for E2B provider")
    
    def get_provider(self, session_id: str) -> Optional[SandboxProvider]:
        """Get provider for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Provider name or None
        """
        return self.session_providers.get(session_id)
