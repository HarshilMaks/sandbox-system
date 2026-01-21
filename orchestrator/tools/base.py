"""Base tool interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolDefinition:
    """Tool definition for function calling."""
    name: str
    description: str
    parameters: Dict
    examples: Optional[list] = None


class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str):
        """Initialize tool.
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with given arguments.
        
        Returns:
            Tool execution result
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict:
        """Get Gemini function calling schema.
        
        Returns:
            Tool schema for function calling
        """
        pass
    
    def validate_args(self, args: Dict) -> bool:
        """Validate tool arguments."""
        return True
