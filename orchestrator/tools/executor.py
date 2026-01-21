"""Tool executor with E2B integration."""
from typing import Dict, Any, List
from orchestrator.tools.registry import ToolRegistry
from orchestrator.tools.implementations import (
    CodeExecutionTool,
    FileOperationsTool,
    WebSearchTool,
    DataAnalysisTool
)
from orchestrator.providers.e2b import E2BProvider
from orchestrator.utils.logging import get_logger


class ToolExecutor:
    """Executes tools with proper error handling and logging."""
    
    def __init__(
        self,
        e2b_provider: E2BProvider,
        registry_path: str = "./registry/tools"
    ):
        """Initialize tool executor.
        
        Args:
            e2b_provider: E2B provider for code execution
            registry_path: Path to tool registry
        """
        self.e2b = e2b_provider
        self.registry = ToolRegistry(registry_path)
        self.logger = get_logger("tools.executor")
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in tool implementations."""
        self.registry.register(CodeExecutionTool(self.e2b))
        self.registry.register(FileOperationsTool(self.e2b))
        self.registry.register(WebSearchTool())
        self.registry.register(DataAnalysisTool(self.e2b))
    
    async def execute(
        self,
        session_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool.
        
        Args:
            session_id: Session identifier
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        self.logger.info(f"Executing tool: {tool_name}")
        
        tool = self.registry.get(tool_name)
        
        if not tool:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}"
            }
        
        try:
            # Validate arguments
            if not tool.validate_args(arguments):
                return {
                    "success": False,
                    "error": f"Invalid arguments for {tool_name}"
                }
            
            # Execute tool
            result = await tool.execute(
                session_id=session_id,
                **arguments
            )
            
            self.logger.info(f"Tool {tool_name} completed: {result.get('success', False)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_tool_schemas(self) -> List[Dict]:
        """Get all tool schemas for function calling."""
        return self.registry.get_schemas()
