"""Tool registry for loading and managing tools."""
import yaml
from pathlib import Path
from typing import Dict, List, Optional

from orchestrator.tools.base import BaseTool
from orchestrator.utils.logging import get_logger


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self, registry_path: str = "./registry/tools"):
        """Initialize tool registry.
        
        Args:
            registry_path: Path to tool definitions
        """
        self.registry_path = Path(registry_path)
        self.tools: Dict[str, BaseTool] = {}
        self.definitions: Dict[str, Dict] = {}
        self.logger = get_logger("tools.registry")
        
        self._load_definitions()
    
    def _load_definitions(self):
        """Load tool definitions from YAML files."""
        if not self.registry_path.exists():
            self.logger.warning(f"Registry path not found: {self.registry_path}")
            return
        
        for yaml_file in self.registry_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    definition = yaml.safe_load(f)
                    
                    if definition and "name" in definition:
                        self.definitions[definition["name"]] = definition
                        self.logger.info(f"Loaded tool definition: {definition['name']}")
            except Exception as e:
                self.logger.error(f"Failed to load {yaml_file}: {e}")
    
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
        schemas = []
        
        for tool in self.tools.values():
            schemas.append(tool.get_schema())
        
        return schemas
    
    def get_definition(self, name: str) -> Optional[Dict]:
        """Get tool definition from YAML."""
        return self.definitions.get(name)
