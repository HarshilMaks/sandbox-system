"""Tests for tool system."""
import pytest
from unittest.mock import MagicMock, patch
import json

from orchestrator.tools.base import BaseTool
from orchestrator.tools.implementations import (
    CodeExecutionTool,
    FileOperationsTool,
    WebSearchTool,
    DataAnalysisTool,
)
from orchestrator.tools.registry import ToolRegistry


class TestBaseTool:
    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            BaseTool("test", "desc")

    def test_concrete_tool(self):
        class ConcreteTool(BaseTool):
            async def execute(self, **kwargs):
                return {"success": True}

            def get_schema(self):
                return {"type": "function", "function": {"name": self.name}}

        tool = ConcreteTool("my_tool", "My tool description")
        assert tool.name == "my_tool"
        assert tool.description == "My tool description"


class TestCodeExecutionTool:
    @pytest.fixture
    def tool(self, mock_e2b_provider):
        return CodeExecutionTool(mock_e2b_provider)

    def test_schema(self, tool):
        schema = tool.get_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "execute_code"
        assert "code" in schema["function"]["parameters"]["properties"]
        assert "code" in schema["function"]["parameters"]["required"]

    async def test_execute_success(self, tool, mock_e2b_provider):
        mock_e2b_provider.get_sandbox.return_value = MagicMock()
        mock_e2b_provider.execute_code.return_value = {
            "success": True, "stdout": "hello", "stderr": "", "error": None, "artifacts": []
        }

        result = await tool.execute(session_id="session-1", code="print('hello')")
        assert result["success"] is True
        assert result["stdout"] == "hello"

    async def test_execute_creates_sandbox_if_missing(self, tool, mock_e2b_provider):
        mock_e2b_provider.get_sandbox.return_value = None
        mock_e2b_provider.execute_code.return_value = {"success": True, "stdout": "", "stderr": "", "error": None, "artifacts": []}

        await tool.execute(session_id="new-session", code="print('test')")
        mock_e2b_provider.create_sandbox.assert_called_once_with("new-session")


class TestFileOperationsTool:
    @pytest.fixture
    def tool(self, mock_e2b_provider):
        return FileOperationsTool(mock_e2b_provider)

    def test_schema(self, tool):
        schema = tool.get_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "file_operations"
        assert set(schema["function"]["parameters"]["properties"].keys()) == {"operation", "path", "content"}
        assert schema["function"]["parameters"]["required"] == ["operation", "path"]

    async def test_read_file(self, tool, mock_e2b_provider):
        mock_e2b_provider.read_file.return_value = b"file content"
        result = await tool.execute(session_id="s1", operation="read", path="/tmp/test.txt")
        assert result["success"] is True
        assert result["content"] == "file content"

    async def test_read_binary_file(self, tool, mock_e2b_provider):
        mock_e2b_provider.read_file.return_value = b"\x00\x01\x02\xff"
        result = await tool.execute(session_id="s1", operation="read", path="/tmp/binary.bin")
        assert result["success"] is True
        assert "<binary data" in result["content"]

    async def test_write_file(self, tool, mock_e2b_provider):
        result = await tool.execute(session_id="s1", operation="write", path="/tmp/test.txt", content="hello")
        assert result["success"] is True
        mock_e2b_provider.write_file.assert_called_once_with("s1", "/tmp/test.txt", b"hello")

    async def test_write_file_no_content(self, tool):
        result = await tool.execute(session_id="s1", operation="write", path="/tmp/test.txt")
        assert result["success"] is False
        assert "Content required" in result["error"]

    async def test_list_files(self, tool, mock_e2b_provider):
        mock_e2b_provider.list_files.return_value = ["file1.txt", "file2.txt"]
        result = await tool.execute(session_id="s1", operation="list", path="/tmp")
        assert result["success"] is True
        assert result["files"] == ["file1.txt", "file2.txt"]

    async def test_unknown_operation(self, tool):
        result = await tool.execute(session_id="s1", operation="compress", path="/tmp")
        assert result["success"] is False
        assert "Unknown operation" in result["error"]


class TestWebSearchTool:
    @pytest.fixture
    def tool(self):
        return WebSearchTool()

    def test_schema(self, tool):
        schema = tool.get_schema()
        assert schema["function"]["name"] == "web_search"
        assert "query" in schema["function"]["parameters"]["properties"]

    async def test_execute_returns_placeholder(self, tool):
        result = await tool.execute(session_id="s1", query="test query")
        assert result["success"] is True
        assert result["query"] == "test query"
        assert len(result["results"]) > 0
        assert "placeholder" in result["results"][0]["snippet"].lower()


class TestDataAnalysisTool:
    @pytest.fixture
    def tool(self, mock_e2b_provider):
        return DataAnalysisTool(mock_e2b_provider)

    def test_schema(self, tool):
        schema = tool.get_schema()
        assert schema["function"]["name"] == "analyze_data"
        props = schema["function"]["parameters"]["properties"]
        assert "file_path" in props
        assert "analysis_type" in props
        assert props["analysis_type"]["enum"] == ["summary", "visualize"]
        assert "correlate" not in props["analysis_type"]["enum"]

    async def test_summary_analysis(self, tool, mock_e2b_provider):
        mock_e2b_provider.get_sandbox.return_value = MagicMock()
        mock_e2b_provider.execute_code.return_value = {"success": True, "stdout": "shape: (100, 5)", "stderr": "", "error": None, "artifacts": []}

        result = await tool.execute(session_id="s1", file_path="/data/test.csv", analysis_type="summary")
        assert result["success"] is True
        assert result["analysis_type"] == "summary"

    async def test_visualize_analysis(self, tool, mock_e2b_provider):
        mock_e2b_provider.get_sandbox.return_value = MagicMock()
        mock_e2b_provider.execute_code.return_value = {"success": True, "stdout": "Visualization saved", "stderr": "", "error": None, "artifacts": ["/tmp/visualization.png"]}

        result = await tool.execute(session_id="s1", file_path="/data/test.csv", analysis_type="visualize")
        assert result["success"] is True
        assert result["analysis_type"] == "visualize"

    async def test_unknown_analysis_type(self, tool):
        result = await tool.execute(session_id="s1", file_path="/data/test.csv", analysis_type="correlate")
        assert result["success"] is False
        assert "Unknown analysis type" in result["error"]


class TestToolRegistry:
    @pytest.fixture
    def registry(self):
        return ToolRegistry()

    def test_register_and_get(self, registry):
        tool = WebSearchTool()
        registry.register(tool)
        assert registry.get("web_search") is tool

    def test_get_nonexistent(self, registry):
        assert registry.get("nonexistent") is None

    def test_list_tools(self, registry):
        registry.register(WebSearchTool())
        registry.register(CodeExecutionTool(MagicMock()))
        tools = registry.list_tools()
        assert "web_search" in tools
        assert "execute_code" in tools

    def test_get_schemas(self, registry):
        registry.register(WebSearchTool())
        schemas = registry.get_schemas()
        assert len(schemas) == 1
        assert schemas[0]["function"]["name"] == "web_search"

    def test_get_definition_nonexistent(self, registry):
        assert registry.get_definition("nope") is None

    def test_duplicate_register_overwrites(self, registry):
        t1 = WebSearchTool()
        t2 = WebSearchTool()
        registry.register(t1)
        registry.register(t2)
        assert registry.get("web_search") is t2
