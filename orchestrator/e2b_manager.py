"""E2B sandbox manager implementation."""
from e2b_code_interpreter import Sandbox
from typing import Optional


class E2BSandboxManager:
    """Manages E2B cloud sandbox lifecycle.
    
    E2B provides cloud-based secure execution environments.
    Alternative to local Docker containers.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize E2B manager.
        
        Args:
            api_key: E2B API key (or set E2B_API_KEY env var)
        """
        self.api_key = api_key
        self.active_sandboxes = {}  # session_id -> sandbox instance
    
    def start_sandbox(self, session_id: str, environment: str = "Python3") -> str:
        """Start an E2B sandbox.
        
        Args:
            session_id: Unique session identifier
            environment: E2B template (Python3, Node, etc.)
            
        Returns:
            E2B sandbox ID
        """
        sandbox = Sandbox(
            api_key=self.api_key,
            template=environment,
            metadata={"session_id": session_id}
        )
        
        self.active_sandboxes[session_id] = sandbox
        return sandbox.id
    
    def execute_code(self, session_id: str, code: str, language: str = "python") -> dict:
        """Execute code in E2B sandbox.
        
        Args:
            session_id: Session identifier
            code: Code to execute
            language: Programming language
            
        Returns:
            Execution result with stdout, stderr, and artifacts
        """
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No active sandbox for session {session_id}")
        
        sandbox = self.active_sandboxes[session_id]
        
        # Execute code
        execution = sandbox.run_code(code)
        
        return {
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
            "error": execution.error,
            "results": execution.results,
            "artifacts": [artifact.name for artifact in execution.artifacts]
        }
    
    def read_file(self, session_id: str, file_path: str) -> bytes:
        """Read file from E2B sandbox.
        
        Args:
            session_id: Session identifier
            file_path: Path to file in sandbox
            
        Returns:
            File contents as bytes
        """
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No active sandbox for session {session_id}")
        
        sandbox = self.active_sandboxes[session_id]
        return sandbox.files.read(file_path)
    
    def write_file(self, session_id: str, file_path: str, content: bytes) -> None:
        """Write file to E2B sandbox.
        
        Args:
            session_id: Session identifier
            file_path: Path to file in sandbox
            content: File contents as bytes
        """
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No active sandbox for session {session_id}")
        
        sandbox = self.active_sandboxes[session_id]
        sandbox.files.write(file_path, content)
    
    def list_files(self, session_id: str, directory: str = "/") -> list:
        """List files in E2B sandbox directory.
        
        Args:
            session_id: Session identifier
            directory: Directory path
            
        Returns:
            List of file names
        """
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No active sandbox for session {session_id}")
        
        sandbox = self.active_sandboxes[session_id]
        return sandbox.files.list(directory)
    
    def stop_sandbox(self, session_id: str) -> bool:
        """Stop and destroy E2B sandbox.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Success status
        """
        if session_id not in self.active_sandboxes:
            return False
        
        try:
            sandbox = self.active_sandboxes[session_id]
            sandbox.close()
            del self.active_sandboxes[session_id]
            return True
        except Exception as e:
            print(f"Error stopping E2B sandbox: {e}")
            return False
    
    def get_sandbox_url(self, session_id: str) -> Optional[str]:
        """Get web URL for E2B sandbox (if available).
        
        Args:
            session_id: Session identifier
            
        Returns:
            Sandbox URL or None
        """
        if session_id not in self.active_sandboxes:
            return None
        
        sandbox = self.active_sandboxes[session_id]
        return sandbox.get_hostname()
