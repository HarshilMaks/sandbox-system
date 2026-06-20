"""Tests for Gemini and E2B providers."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json


class TestGeminiProvider:
    @pytest.fixture
    def provider(self):
        with patch("orchestrator.providers.gemini.genai") as mock_genai:
            from orchestrator.providers.gemini import GeminiProvider
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client
            provider = GeminiProvider(api_key="test-key")
            provider.client = mock_client
            yield provider

    def test_init_with_env_var(self):
        with patch("orchestrator.providers.gemini.genai"), \
             patch("orchestrator.providers.gemini.os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda k, d=None: {"GEMINI_API_KEY": "env-key", "GEMINI_MODEL": "gemini-pro"}.get(k, d)
            from orchestrator.providers.gemini import GeminiProvider
            provider = GeminiProvider()
            assert provider.api_key == "env-key"
            # Provider creates client in __init__, which we mocked, so we can check model
            assert provider.model == "gemini-pro"

    def test_init_raises_on_missing_key(self):
        with patch("orchestrator.providers.gemini.os.getenv", return_value=None):
            from orchestrator.providers.gemini import GeminiProvider
            with pytest.raises(ValueError, match="Gemini API key is required"):
                GeminiProvider()

    def test_convert_messages_basic(self, provider):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi", "tool_calls": []},
        ]
        contents = provider._convert_messages(messages)
        assert len(contents) == 2
        assert contents[0]["role"] == "user"
        assert contents[0]["parts"][0]["text"] == "Hello"
        assert contents[1]["role"] == "model"
        assert contents[1]["parts"][0]["text"] == "Hi"

    def test_convert_messages_with_tool_calls(self, provider):
        messages = [
            {"role": "assistant", "content": "Let me search",
             "tool_calls": [{
                 "id": "call_1",
                 "function": {"name": "web_search", "arguments": '{"query": "test"}'}
             }]},
        ]
        contents = provider._convert_messages(messages)
        assert len(contents) == 1
        assert contents[0]["role"] == "model"
        assert len(contents[0]["parts"]) == 2
        # First part is text
        assert contents[0]["parts"][0]["text"] == "Let me search"
        # Second part is function_call
        assert "function_call" in contents[0]["parts"][1]
        assert contents[0]["parts"][1]["function_call"]["name"] == "web_search"

    def test_convert_messages_with_tool_results(self, provider):
        messages = [
            {"role": "tool", "tool_call_id": "call_1", "content": '{"result": "data"}'},
        ]
        contents = provider._convert_messages(messages)
        assert len(contents) == 1
        assert contents[0]["role"] == "user"
        assert "Tool result:" in contents[0]["parts"][0]["text"]

    def test_convert_messages_skips_empty_assistant(self, provider):
        messages = [
            {"role": "assistant", "content": "", "tool_calls": []},
        ]
        contents = provider._convert_messages(messages)
        assert contents == []

    def test_convert_tools(self, provider):
        tools = [{
            "type": "function",
            "function": {
                "name": "test_fn",
                "description": "A test function",
                "parameters": {"type": "object", "properties": {"x": {"type": "string"}}}
            }
        }]
        result = provider._convert_tools(tools)
        assert result is not None
        assert len(result.function_declarations) == 1
        assert result.function_declarations[0].name == "test_fn"

    def test_convert_tools_empty(self, provider):
        assert provider._convert_tools([]) is None

    def test_chat_completion_with_system_prompt(self, provider):
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
        ]
        mock_response = MagicMock()
        mock_response.text = "Hi there"
        mock_response.candidates = []
        provider.client.models.generate_content.return_value = mock_response

        import asyncio
        result = asyncio.run(provider.chat_completion(messages=messages))

        assert result["content"] == "Hi there"
        call_kwargs = provider.client.models.generate_content.call_args.kwargs
        assert call_kwargs["contents"] == [{"role": "user", "parts": [{"text": "Hello"}]}]
        config = call_kwargs["config"]
        assert config.system_instruction == "You are helpful"
