"""Tests for ConversationManager."""
import pytest
from datetime import datetime, timezone

from orchestrator.core.conversation import ConversationManager
from orchestrator.core.memory import MemoryStore


class TestConversationManager:
    @pytest.fixture
    async def manager(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        return ConversationManager(store, max_history=10)

    def test_init(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        manager = ConversationManager(store, max_history=50)
        assert manager.max_history == 50
        assert manager.memory is store

    @pytest.mark.asyncio
    async def test_add_and_get_messages(self, manager):
        await manager.add_message("session-1", "user", "Hello")
        await manager.add_message("session-1", "assistant", "Hi there")

        messages = await manager.get_messages("session-1")
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hi there"

    @pytest.mark.asyncio
    async def test_get_messages_empty_session(self, manager):
        messages = await manager.get_messages("nonexistent")
        assert messages == []

    @pytest.mark.asyncio
    async def test_max_history(self, manager):
        for i in range(15):
            await manager.add_message("session-1", "user", f"msg {i}")
            await manager.add_message("session-1", "assistant", f"resp {i}")

        messages = await manager.get_messages("session-1")
        assert len(messages) == 10

    @pytest.mark.asyncio
    async def test_get_context(self, manager):
        await manager.add_message("session-1", "user", "First message")
        await manager.add_message("session-1", "assistant", "First response")
        await manager.add_message("session-1", "user", "Second message")
        await manager.add_message("session-1", "assistant", "Second response")

        context = await manager.get_context("session-1", window=2)
        assert len(context.split("\n")) == 2

    @pytest.mark.asyncio
    async def test_get_context_window(self, manager):
        for i in range(5):
            await manager.add_message("session-1", "user", f"msg {i}")
            await manager.add_message("session-1", "assistant", f"resp {i}")

        context = await manager.get_context("session-1", window=2)
        lines = context.split("\n")
        assert len(lines) == 2
        assert "msg 4" in lines[0]
        assert "resp 4" in lines[1]

    @pytest.mark.asyncio
    async def test_clear_session(self, manager):
        await manager.add_message("session-1", "user", "Hello")
        await manager.clear_session("session-1")
        messages = await manager.get_messages("session-1")
        assert messages == []

    @pytest.mark.asyncio
    async def test_session_isolation(self, manager):
        await manager.add_message("session-a", "user", "Hello A")
        await manager.add_message("session-b", "user", "Hello B")

        msgs_a = await manager.get_messages("session-a")
        msgs_b = await manager.get_messages("session-b")

        assert len(msgs_a) == 1
        assert len(msgs_b) == 1
        assert msgs_a[0]["content"] == "Hello A"
        assert msgs_b[0]["content"] == "Hello B"

    @pytest.mark.asyncio
    async def test_get_summary(self, manager):
        await manager.add_message("session-1", "user", "Hello")
        await manager.add_message("session-1", "assistant", "Hi")
        await manager.add_message("session-1", "user", "How are you?")

        summary = await manager.get_summary("session-1")
        assert summary["message_count"] == 3
        assert summary["user_messages"] == 2
        assert summary["assistant_messages"] == 1
        assert summary["duration_seconds"] is not None

    @pytest.mark.asyncio
    async def test_get_summary_empty(self, manager):
        summary = await manager.get_summary("empty-session")
        assert summary["message_count"] == 0

    @pytest.mark.asyncio
    async def test_invalid_session_id_path_traversal(self, manager):
        with pytest.raises(ValueError, match="Invalid session_id"):
            await manager.get_messages("../etc/passwd")

    @pytest.mark.asyncio
    async def test_invalid_session_id_dots(self, manager):
        with pytest.raises(ValueError, match="Invalid session_id"):
            await manager.add_message("../../etc", "user", "bad")

    @pytest.mark.asyncio
    async def test_invalid_session_id_empty(self, manager):
        with pytest.raises(ValueError, match="Invalid session_id"):
            await manager.get_messages("")

    @pytest.mark.asyncio
    async def test_invalid_session_id_clear(self, manager):
        with pytest.raises(ValueError, match="Invalid session_id"):
            await manager.clear_session("../escape")

    @pytest.mark.asyncio
    async def test_messages_have_timestamp(self, manager):
        await manager.add_message("session-1", "user", "Hello")
        messages = await manager.get_messages("session-1")
        assert "timestamp" in messages[0]
        assert messages[0]["timestamp"] is not None

    @pytest.mark.asyncio
    async def test_messages_have_metadata(self, manager):
        meta = {"source": "test"}
        await manager.add_message("session-1", "user", "Hello", metadata=meta)
        messages = await manager.get_messages("session-1")
        assert messages[0]["metadata"] == meta
