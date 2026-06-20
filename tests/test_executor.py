"""Tests for ToolExecutor."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from orchestrator.tools.executor import ToolExecutor
from orchestrator.tools.base import BaseTool


class TestToolExecutor:
    @pytest.fixture
    def executor(self, mock_e2b_provider):
        with patch("orchestrator.tools.executor.ToolRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_registry_cls.return_value = mock_registry

            executor = ToolExecutor(mock_e2b_provider, registry_path="./registry/tools")
            executor.registry = mock_registry
            yield executor

    async def test_execute_existing_tool(self, executor):
        mock_tool = MagicMock(spec=BaseTool)
        mock_tool.execute = AsyncMock(return_value={"success": True, "result": "done"})
        mock_tool.validate_args = MagicMock(return_value=True)
        executor.registry.get.return_value = mock_tool

        result = await executor.execute(session_id="s1", tool_name="test_tool", arguments={"arg1": "val1"})
        assert result["success"] is True
        mock_tool.execute.assert_called_once_with(session_id="s1", arg1="val1")

    async def test_execute_nonexistent_tool(self, executor):
        executor.registry.get.return_value = None
        result = await executor.execute(session_id="s1", tool_name="nope", arguments={})
        assert result["success"] is False
        assert "not found" in result["error"]

    async def test_execute_with_invalid_args(self, executor):
        mock_tool = MagicMock(spec=BaseTool)
        mock_tool.validate_args.return_value = False
        executor.registry.get.return_value = mock_tool

        result = await executor.execute(session_id="s1", tool_name="bad_tool", arguments={"bad": "args"})
        assert result["success"] is False
        assert "Invalid arguments" in result["error"]

    async def test_execute_handles_exception(self, executor):
        mock_tool = MagicMock(spec=BaseTool)
        mock_tool.execute = AsyncMock(side_effect=RuntimeError("boom"))
        mock_tool.validate_args.return_value = True
        executor.registry.get.return_value = mock_tool

        result = await executor.execute(session_id="s1", tool_name="broken", arguments={})
        assert result["success"] is False
        assert "boom" in result["error"]

    def test_get_tool_schemas(self, executor):
        executor.registry.get_schemas.return_value = [{"name": "tool1"}]
        schemas = executor.get_tool_schemas()
        assert schemas == [{"name": "tool1"}]

    def test_register_builtin_tools(self, mock_e2b_provider):
        with patch("orchestrator.tools.executor.ToolRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_registry_cls.return_value = mock_registry

            executor = ToolExecutor(mock_e2b_provider, registry_path="./registry/tools")
            expected_tools = {"execute_code", "file_operations", "web_search", "analyze_data"}
            registered_names = {call.args[0].name for call in mock_registry.register.call_args_list}
            assert registered_names == expected_tools
