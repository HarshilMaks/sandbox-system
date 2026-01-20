"""E2B sandbox routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CodeExecutionRequest(BaseModel):
    session_id: str
    code: str
    language: str = "python"


class FileUploadRequest(BaseModel):
    session_id: str
    file_path: str
    content: str  # Base64 encoded


@router.post("/execute")
def execute_code(request: CodeExecutionRequest):
    """Execute code in E2B sandbox.
    
    Args:
        request: Code execution request
        
    Returns:
        Execution results with stdout, stderr, artifacts
    """
    # Implementation would call UnifiedSandboxManager.execute_code()
    return {
        "stdout": "Hello from E2B",
        "stderr": "",
        "error": None,
        "results": [],
        "artifacts": []
    }


@router.get("/files/{session_id}")
def list_files(session_id: str, directory: str = "/"):
    """List files in E2B sandbox.
    
    Args:
        session_id: Session identifier
        directory: Directory path
        
    Returns:
        List of files
    """
    # Implementation would call E2BSandboxManager.list_files()
    return {
        "session_id": session_id,
        "directory": directory,
        "files": ["example.py", "data.csv"]
    }


@router.get("/files/{session_id}/{file_path:path}")
def read_file(session_id: str, file_path: str):
    """Read file from E2B sandbox.
    
    Args:
        session_id: Session identifier
        file_path: Path to file
        
    Returns:
        File contents
    """
    # Implementation would call E2BSandboxManager.read_file()
    return {
        "session_id": session_id,
        "file_path": file_path,
        "content": "# File content here"
    }


@router.post("/files")
def write_file(request: FileUploadRequest):
    """Write file to E2B sandbox.
    
    Args:
        request: File upload request
        
    Returns:
        Success status
    """
    # Implementation would call E2BSandboxManager.write_file()
    return {
        "status": "success",
        "file_path": request.file_path
    }


@router.get("/url/{session_id}")
def get_sandbox_url(session_id: str):
    """Get web URL for E2B sandbox.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Sandbox URL
    """
    # Implementation would call E2BSandboxManager.get_sandbox_url()
    return {
        "session_id": session_id,
        "url": "https://sandbox-xyz.e2b.dev"
    }
