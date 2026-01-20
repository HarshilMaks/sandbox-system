"""Built-in tool implementations."""
from typing import Dict, Any
from orchestrator.tools.base import BaseTool
from orchestrator.providers.e2b import E2BProvider
import json


class CodeExecutionTool(BaseTool):
    """Execute Python code in E2B sandbox."""
    
    def __init__(self, e2b_provider: E2BProvider):
        super().__init__(
            name="execute_code",
            description="Execute Python code in secure sandbox. Returns stdout, stderr, and any generated artifacts."
        )
        self.e2b = e2b_provider
    
    async def execute(self, session_id: str, code: str, **kwargs) -> Dict[str, Any]:
        """Execute code in E2B sandbox."""
        # Ensure sandbox exists
        if not self.e2b.get_sandbox(session_id):
            self.e2b.create_sandbox(session_id)
        
        result = self.e2b.execute_code(session_id, code)
        
        return {
            "success": result["success"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "error": result.get("error"),
            "artifacts": result.get("artifacts", [])
        }
    
    def get_schema(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute"
                        }
                    },
                    "required": ["code"]
                }
            }
        }


class FileOperationsTool(BaseTool):
    """File operations in E2B sandbox."""
    
    def __init__(self, e2b_provider: E2BProvider):
        super().__init__(
            name="file_operations",
            description="Read, write, or list files in the sandbox filesystem"
        )
        self.e2b = e2b_provider
    
    async def execute(
        self,
        session_id: str,
        operation: str,
        path: str,
        content: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute file operation."""
        if operation == "read":
            data = self.e2b.read_file(session_id, path)
            return {
                "success": True,
                "content": data.decode('utf-8'),
                "path": path
            }
        
        elif operation == "write":
            if not content:
                return {"success": False, "error": "Content required for write"}
            
            self.e2b.write_file(session_id, path, content.encode('utf-8'))
            return {
                "success": True,
                "path": path,
                "message": f"File written to {path}"
            }
        
        elif operation == "list":
            files = self.e2b.list_files(session_id, path)
            return {
                "success": True,
                "files": files,
                "directory": path
            }
        
        return {"success": False, "error": f"Unknown operation: {operation}"}
    
    def get_schema(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["read", "write", "list"],
                            "description": "File operation to perform"
                        },
                        "path": {
                            "type": "string",
                            "description": "File or directory path"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write (for write operation)"
                        }
                    },
                    "required": ["operation", "path"]
                }
            }
        }


class WebSearchTool(BaseTool):
    """Web search tool (placeholder)."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information"
        )
    
    async def execute(self, session_id: str, query: str, **kwargs) -> Dict[str, Any]:
        """Execute web search."""
        # Placeholder - would integrate with search API in production
        return {
            "success": True,
            "results": [
                {
                    "title": f"Search result for: {query}",
                    "snippet": "This is a placeholder. Integrate with real search API.",
                    "url": "https://example.com"
                }
            ],
            "query": query
        }
    
    def get_schema(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }


class DataAnalysisTool(BaseTool):
    """Data analysis with pandas."""
    
    def __init__(self, e2b_provider: E2BProvider):
        super().__init__(
            name="analyze_data",
            description="Analyze CSV/Excel data with pandas - get summary statistics, correlations, visualizations"
        )
        self.e2b = e2b_provider
    
    async def execute(
        self,
        session_id: str,
        file_path: str,
        analysis_type: str = "summary",
        **kwargs
    ) -> Dict[str, Any]:
        """Execute data analysis."""
        # Generate pandas code based on analysis type
        if analysis_type == "summary":
            code = f"""
import pandas as pd
df = pd.read_csv('{file_path}')
print("Shape:", df.shape)
print("\\nColumn Types:")
print(df.dtypes)
print("\\nSummary Statistics:")
print(df.describe())
print("\\nMissing Values:")
print(df.isnull().sum())
"""
        elif analysis_type == "visualize":
            code = f"""
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('{file_path}')
df.hist(figsize=(12, 8), bins=20)
plt.tight_layout()
plt.savefig('/tmp/visualization.png')
print("Visualization saved to /tmp/visualization.png")
"""
        else:
            return {"success": False, "error": f"Unknown analysis type: {analysis_type}"}
        
        # Ensure sandbox exists
        if not self.e2b.get_sandbox(session_id):
            self.e2b.create_sandbox(session_id)
        
        result = self.e2b.execute_code(session_id, code)
        
        return {
            "success": result["success"],
            "analysis_type": analysis_type,
            "output": result["stdout"],
            "error": result.get("error"),
            "artifacts": result.get("artifacts", [])
        }
    
    def get_schema(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to CSV/Excel file"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["summary", "visualize", "correlate"],
                            "description": "Type of analysis to perform"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        }
