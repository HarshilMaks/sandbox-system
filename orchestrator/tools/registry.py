"""Tool registry for managing available tools."""
from typing import Dict, List, Optional

from orchestrator.tools.base import BaseTool
from orchestrator.utils.logging import get_logger


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, BaseTool] = {}
        self.logger = get_logger("tools.registry")
    
    def register(self, tool: BaseTool):
        """Register a tool instance.
        
        Args:
            tool: Tool to register
        """
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_schemas(self) -> List[Dict]:
        """Get all tool schemas for function calling.
        
        Returns:
            List of OpenAI function schemas
        """
        return [tool.get_schema() for tool in self.tools.values()]
