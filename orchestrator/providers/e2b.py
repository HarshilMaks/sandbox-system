"""E2B provider for code execution."""
import os
from typing import Optional, Dict, Any
from e2b_code_interpreter import Sandbox

from orchestrator.utils.logging import get_logger
from orchestrator.utils.retry import with_retry


class E2BProvider:
    """E2B sandbox provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize E2B provider.
        
        Args:
            api_key: E2B API key (or use E2B_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("E2B_API_KEY")
        self.logger = get_logger("provider.e2b")
        self.sandboxes: Dict[str, Sandbox] = {}
    
    # Custom template with pre-installed packages (numpy, pandas, sklearn, matplotlib)
    DEFAULT_TEMPLATE = "en7sb4k1n268scs49jnj"
    
    @with_retry(max_attempts=2)
    def create_sandbox(self, session_id: str, template: Optional[str] = None) -> str:
        """Create E2B sandbox.
        
        Args:
            session_id: Session identifier
            template: E2B template ID (optional, uses custom template with pre-installed packages)
                     Set to "default" to use E2B's basic template without packages
            
        Returns:
            Sandbox ID
        """
        self.logger.info(f"Creating sandbox for session {session_id}")
        
        # Use custom template by default (has numpy, pandas, sklearn, matplotlib pre-installed)
        if template == "default":
            self.logger.info("Using default E2B template (no pre-installed packages)")
            sandbox = Sandbox(api_key=self.api_key)
        else:
            template = template or self.DEFAULT_TEMPLATE
            self.logger.info(f"Using custom template: {template}")
            sandbox = Sandbox(
                template=template,
                api_key=self.api_key
            )
        
        self.sandboxes[session_id] = sandbox
        self.logger.info(f"Sandbox created: {sandbox.sandbox_id}")
        
        return sandbox.sandbox_id
    
    def get_sandbox(self, session_id: str) -> Optional[Sandbox]:
        """Get existing sandbox."""
        return self.sandboxes.get(session_id)
    
    @with_retry(max_attempts=2)
    def execute_code(
        self,
        session_id: str,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """Execute code in sandbox.
        
        Args:
            session_id: Session identifier
            code: Code to execute
            language: Programming language
            
        Returns:
            Execution result
        """
        sandbox = self.get_sandbox(session_id)
        
        if not sandbox:
            raise ValueError(f"No sandbox found for session {session_id}")
        
        self.logger.info(f"Executing code in session {session_id}")
        
        execution = sandbox.run_code(code)
        
        result = {
            "success": not bool(execution.error),
            "stdout": execution.logs.stdout if execution.logs else "",
            "stderr": execution.logs.stderr if execution.logs else "",
            "error": str(execution.error) if execution.error else None,
            "artifacts": []
        }
        
        # Extract artifacts (charts, images, etc.)
        if execution.results:
            for res in execution.results:
                if hasattr(res, "png"):
                    result["artifacts"].append({
                        "type": "image/png",
                        "data": res.png
                    })
        
        return result
    
    def write_file(
        self,
        session_id: str,
        path: str,
        content: bytes
    ):
        """Write file to sandbox."""
        sandbox = self.get_sandbox(session_id)
        if sandbox:
            sandbox.files.write(path, content)
            self.logger.info(f"Wrote file: {path}")
    
    def read_file(
        self,
        session_id: str,
        path: str
    ) -> bytes:
        """Read file from sandbox."""
        sandbox = self.get_sandbox(session_id)
        if sandbox:
            return sandbox.files.read(path)
        raise ValueError(f"No sandbox for session {session_id}")
    
    def list_files(
        self,
        session_id: str,
        directory: str = "/"
    ) -> list:
        """List files in sandbox directory."""
        sandbox = self.get_sandbox(session_id)
        if sandbox:
            files = sandbox.files.list(directory)
            return [f.name for f in files]
        return []
    
    def close_sandbox(self, session_id: str):
        """Close sandbox."""
        sandbox = self.sandboxes.pop(session_id, None)
        if sandbox:
            try:
                sandbox.kill()
                self.logger.info(f"Closed sandbox for session {session_id}")
            except Exception as e:
                self.logger.warning(f"Error closing sandbox {session_id}: {e}")
    
    def cleanup_all(self):
        """Close all sandboxes."""
        for session_id in list(self.sandboxes.keys()):
            self.close_sandbox(session_id)
