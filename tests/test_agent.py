"""Tests for Agent and AgentConfig."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from orchestrator.core.agent import Agent, AgentConfig, AgentResponse
from orchestrator.core.memory import MemoryStore


class TestAgentConfig:
    def test_default_values(self):
        config = AgentConfig(name="test")
        assert config.name == "test"
        assert config.model == "gemini-2.0-flash-exp"
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.system_prompt is None
        assert config.tools_enabled is True
        assert config.streaming is False
        assert config.max_iterations == 10
        assert config.timeout == 300

    def test_custom_values(self):
        config = AgentConfig(
            name="custom",
            model="gemini-2.0-flash-exp",
            temperature=0.5,
            max_tokens=1000,
            system_prompt="Be helpful",
            tools_enabled=False,
            streaming=True,
            max_iterations=5,
            timeout=60
        )
        assert config.name == "custom"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.max_iterations == 5
        assert config.timeout == 60


class TestAgentResponse:
    def test_default_fields(self):
        resp = AgentResponse(content="Hello")
        assert resp.content == "Hello"
        assert resp.tool_calls == []
        assert resp.metadata == {}
        assert resp.usage is None
        assert isinstance(resp.timestamp, datetime)

    def test_timestamp_is_utc(self):
        resp = AgentResponse(content="test")
        assert resp.timestamp.tzinfo is not None
        assert resp.timestamp.tzinfo == timezone.utc

    def test_with_tool_calls(self):
        resp = AgentResponse(
            content="",
            tool_calls=[{"function": {"name": "test_fn"}}],
            usage={"total_tokens": 42}
        )
        assert len(resp.tool_calls) == 1
        assert resp.usage["total_tokens"] == 42

    def test_with_metadata(self):
        resp = AgentResponse(content="done", metadata={"iterations": 3})
        assert resp.metadata["iterations"] == 3


class TestAgent:
    @pytest.fixture
    async def agent(self, mock_gemini_provider, mock_tool_executor, temp_storage_dir):
        config = AgentConfig(
            name="test-agent",
            system_prompt="You are a test assistant"
        )
        memory_store = MemoryStore(storage_dir=temp_storage_dir)
        return Agent(
            config=config,
            llm_provider=mock_gemini_provider,
            tool_executor=mock_tool_executor,
            memory_store=memory_store
        )

    async def test_run_returns_response(self, agent):
        response = await agent.run(message="Hello", session_id="test-session")
        assert isinstance(response, AgentResponse)
        assert response.content == "Test response"

    async def test_run_with_tool_calls(self, agent, mock_gemini_provider):
        mock_gemini_provider.chat_completion.return_value = {
            "content": "",
            "role": "assistant",
            "tool_calls": [{
                "id": "call_1",
                "function": {"name": "test_tool", "arguments": "{}"}
            }],
            "usage": {"total_tokens": 20}
        }

        agent.tools = MagicMock()
        agent.tools.execute = AsyncMock(return_value={"success": True, "result": "tool output"})
        agent.tools.get_tool_schemas = MagicMock(return_value=[{"type": "function", "function": {"name": "test_tool"}}])

        response = await agent.run(message="Use a tool", session_id="test-session")
        assert response.tool_calls is not None
        assert agent.tools.execute.called

    async def test_run_saves_to_memory(self, agent):
        await agent.run(message="Remember this", session_id="test-session")
        messages = await agent.conversation.get_messages("test-session")
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Remember this"
        assert messages[1]["role"] == "assistant"

    async def test_run_multiple_turns(self, agent):
        await agent.run(message="First", session_id="multi-turn")
        await agent.run(message="Second", session_id="multi-turn")

        messages = await agent.conversation.get_messages("multi-turn")
        assert len(messages) == 4
        assert messages[2]["content"] == "Second"

    async def test_reset_session(self, agent):
        await agent.run(message="Hello", session_id="reset-session")
        await agent.reset_session("reset-session")
        messages = await agent.conversation.get_messages("reset-session")
        assert messages == []

    async def test_session_isolation(self, agent):
        await agent.run(message="Session A", session_id="session-a")
        await agent.run(message="Session B", session_id="session-b")

        msgs_a = await agent.conversation.get_messages("session-a")
        msgs_b = await agent.conversation.get_messages("session-b")
        assert len(msgs_a) == 2
        assert len(msgs_b) == 2

    async def test_system_prompt_included_every_turn(self, agent):
        await agent.run(message="Turn 1", session_id="sys-prompt-test")
        await agent.run(message="Turn 2", session_id="sys-prompt-test")

        assert agent.llm.chat_completion.call_count == 2
        for call in agent.llm.chat_completion.call_args_list:
            messages = call.kwargs["messages"]
            system_msgs = [m for m in messages if m["role"] == "system"]
            assert len(system_msgs) == 1
            assert system_msgs[0]["content"] == "You are a test assistant"

    async def test_no_tools_when_disabled(self, mock_gemini_provider, temp_storage_dir):
        config = AgentConfig(name="no-tools", tools_enabled=False)
        agent = Agent(config=config, llm_provider=mock_gemini_provider)
        await agent.run(message="Hello", session_id="test")

        call_kwargs = mock_gemini_provider.chat_completion.call_args.kwargs
        assert call_kwargs["tools"] is None

    async def test_invalid_session_id(self, agent):
        with pytest.raises(ValueError, match="Invalid session_id"):
            await agent.run(message="Hello", session_id="../bad")

    async def test_stream_method(self, agent):
        async def mock_stream(messages, model):
            yield "chunk1"
            yield "chunk2"
        agent.llm.stream_completion = mock_stream

        chunks = []
        async for chunk in agent.stream(message="Hello", session_id="stream-test"):
            chunks.append(chunk)
        assert chunks == ["chunk1", "chunk2"]

    async def test_iteration_count(self, agent, mock_gemini_provider):
        response = await agent.run(message="Hello", session_id="test")
        assert "iterations" in response.metadata
        assert response.metadata["iterations"] >= 1
