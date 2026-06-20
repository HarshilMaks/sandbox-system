"""Shared test fixtures and mocks."""
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import json

from unittest.mock import MagicMock as _Mock
import types as _types_mod

# Mock external deps before any module imports them
sys.modules["google"] = _Mock()
sys.modules["google.genai"] = _Mock()

_types_module = _types_mod.ModuleType("google.genai.types")

class GenerateContentConfig:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class FunctionDeclaration:
    def __init__(self, name="", description="", parameters=None):
        self.name = name
        self.description = description
        self.parameters = parameters

class Tool:
    def __init__(self, function_declarations=None):
        self.function_declarations = function_declarations or []

_types_module.GenerateContentConfig = GenerateContentConfig
_types_module.FunctionDeclaration = FunctionDeclaration
_types_module.Tool = Tool
sys.modules["google.genai.types"] = _types_module

sys.modules["e2b_code_interpreter"] = _Mock()


@pytest.fixture
def temp_storage_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_gemini_provider():
    """Create a mock GeminiProvider that returns predictable responses."""
    with patch("orchestrator.providers.gemini.GeminiProvider", autospec=True) as mock:
        provider = mock.return_value
        provider.chat_completion = AsyncMock(return_value={
            "content": "Test response",
            "role": "assistant",
            "tool_calls": [],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        })
        provider.stream_completion = AsyncMock()
        provider.model = "gemini-2.0-flash-exp"
        yield provider


@pytest.fixture
def mock_e2b_provider():
    """Create a mock E2BProvider."""
    with patch("orchestrator.providers.e2b.E2BProvider", autospec=True) as mock:
        provider = mock.return_value
        provider.create_sandbox = MagicMock(return_value="sandbox-id")
        provider.get_sandbox = MagicMock(return_value=MagicMock())
        provider.execute_code = MagicMock(return_value={
            "success": True, "stdout": "output", "stderr": "", "error": None, "artifacts": []
        })
        provider.close_sandbox = MagicMock()
        yield provider


@pytest.fixture
def mock_tool_executor():
    """Create a mock ToolExecutor."""
    with patch("orchestrator.tools.executor.ToolExecutor", autospec=True) as mock:
        executor = mock.return_value
        execute_result = {"success": True, "result": "mock output"}
        executor.execute = AsyncMock(return_value=execute_result)
        executor.get_tool_schemas = MagicMock(return_value=[])
        yield executor


@pytest.fixture
def sample_conversation_history():
    return [
        {"role": "user", "content": "Hello", "timestamp": "2025-01-01T00:00:00", "metadata": {}},
        {"role": "assistant", "content": "Hi there!", "timestamp": "2025-01-01T00:00:01", "metadata": {}},
    ]
