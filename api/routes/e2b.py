"""E2B sandbox routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import base64
from orchestrator.unified_manager import UnifiedSandboxManager

router = APIRouter()

# Initialize E2B manager
manager = UnifiedSandboxManager(e2b_api_key=os.getenv("E2B_API_KEY"))


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
    try:
        result = manager.execute_code(
            session_id=request.session_id,
            code=request.code,
            language=request.language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{session_id}")
def list_files(session_id: str, directory: str = "/"):
    """List files in E2B sandbox.
    
    Args:
        session_id: Session identifier
        directory: Directory path
        
    Returns:
        List of files
    """
    try:
        provider = manager.get_provider(session_id)
        if provider != "e2b":
            raise HTTPException(status_code=400, detail="Only E2B sessions support file listing")
        
        files = manager.e2b_manager.list_files(session_id, directory)
        return {
            "session_id": session_id,
            "directory": directory,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{session_id}/{file_path:path}")
def read_file(session_id: str, file_path: str):
    """Read file from E2B sandbox.
    
    Args:
        session_id: Session identifier
        file_path: Path to file
        
    Returns:
        File contents
    """
    try:
        provider = manager.get_provider(session_id)
        if provider != "e2b":
            raise HTTPException(status_code=400, detail="Only E2B sessions support file reading")
        
        content = manager.e2b_manager.read_file(session_id, file_path)
        return {
            "session_id": session_id,
            "file_path": file_path,
            "content": base64.b64encode(content).decode('utf-8'),
            "encoding": "base64"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files")
def write_file(request: FileUploadRequest):
    """Write file to E2B sandbox.
    
    Args:
        request: File upload request
        
    Returns:
        Success status
    """
    try:
        provider = manager.get_provider(request.session_id)
        if provider != "e2b":
            raise HTTPException(status_code=400, detail="Only E2B sessions support file writing")
        
        # Decode base64 content
        content = base64.b64decode(request.content)
        manager.e2b_manager.write_file(request.session_id, request.file_path, content)
        
        return {
            "status": "success",
            "file_path": request.file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/url/{session_id}")
def get_sandbox_url(session_id: str):
    """Get web URL for E2B sandbox.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Sandbox URL
    """
    try:
        provider = manager.get_provider(session_id)
        if provider != "e2b":
            raise HTTPException(status_code=400, detail="Only E2B sessions have URLs")
        
        url = manager.e2b_manager.get_sandbox_url(session_id)
        return {
            "session_id": session_id,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
