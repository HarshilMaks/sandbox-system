"""Tests for MemoryStore and KeywordMemory."""
import pytest
import json
import base64
from pathlib import Path
from datetime import datetime, timezone

from orchestrator.core.memory import MemoryStore, KeywordMemory


class TestMemoryStore:
    async def test_set_and_get(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("key1", "value1")
        assert await store.get("key1") == "value1"

    async def test_get_default(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        assert await store.get("nonexistent", "default") == "default"

    async def test_delete(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("key1", "value1")
        await store.delete("key1")
        assert await store.get("key1") is None

    async def test_exists(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("key1", "value1")
        assert await store.exists("key1") is True
        assert await store.exists("nonexistent") is False

    async def test_keys(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("alpha", 1)
        await store.set("beta", 2)
        await store.set("gamma", 3)
        keys = await store.keys()
        assert sorted(keys) == ["alpha", "beta", "gamma"]

    async def test_keys_with_pattern(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("apple", 1)
        await store.set("banana", 2)
        await store.set("apricot", 3)
        keys = await store.keys(pattern="ap")
        assert sorted(keys) == ["apple", "apricot"]

    async def test_ttl_expiry(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("key1", "value1", ttl_seconds=-1)
        assert await store.get("key1") is None

    async def test_clear(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("key1", "value1")
        await store.set("key2", "value2")
        await store.clear()
        assert await store.keys() == []

    async def test_persistence_to_disk(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("persist:key", {"data": 42})

        files = list(Path(temp_storage_dir).glob("*.json"))
        assert len(files) == 1

        loaded = MemoryStore(storage_dir=temp_storage_dir)
        assert await loaded.get("persist:key") == {"data": 42}

    async def test_collision_free_keys(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("conv:test", "a")
        await store.set("conv_test", "b")

        assert await store.get("conv:test") == "a"
        assert await store.get("conv_test") == "b"

        store2 = MemoryStore(storage_dir=temp_storage_dir)
        assert await store2.get("conv:test") == "a"
        assert await store2.get("conv_test") == "b"

    async def test_round_trip_complex_keys(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.set("user/session:123", "path test")
        await store.set("a:b/c:d", "multi sep")

        store2 = MemoryStore(storage_dir=temp_storage_dir)
        assert await store2.get("user/session:123") == "path test"
        assert await store2.get("a:b/c:d") == "multi sep"

    async def test_safe_key_encoding(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        key = "special:chars/and spaces"
        safe = store._safe_key(key)
        assert "/" not in safe
        assert ":" not in safe
        assert " " not in safe

    async def test_memory_disabled_no_storage_dir(self):
        store = MemoryStore(storage_dir=None)
        await store.set("key1", "value1")
        assert await store.get("key1") == "value1"
        assert store.storage_dir is None

    async def test_delete_nonexistent(self, temp_storage_dir):
        store = MemoryStore(storage_dir=temp_storage_dir)
        await store.delete("nonexistent")
        assert await store.get("nonexistent") is None


class TestKeywordMemory:
    async def test_add_and_search(self):
        mem = KeywordMemory()
        await mem.add("The quick brown fox")
        await mem.add("Jumped over the lazy dog")
        results = await mem.search("fox")
        assert len(results) == 1
        assert "fox" in results[0]["text"]

    async def test_search_multiple_matches(self):
        mem = KeywordMemory()
        await mem.add("Python programming")
        await mem.add("Python is great")
        await mem.add("Java is different")
        results = await mem.search("Python")
        assert len(results) == 2

    async def test_search_no_match(self):
        mem = KeywordMemory()
        await mem.add("Hello world")
        results = await mem.search("nonexistent")
        assert results == []

    async def test_search_respects_limit(self):
        mem = KeywordMemory()
        for i in range(10):
            await mem.add(f"Document number {i} about Python")
        results = await mem.search("Python", limit=3)
        assert len(results) == 3

    async def test_add_with_metadata(self):
        mem = KeywordMemory()
        await mem.add("Important note", metadata={"priority": "high"})
        results = await mem.search("Important")
        assert len(results) == 1
        assert results[0]["metadata"]["priority"] == "high"

    async def test_empty_store(self):
        mem = KeywordMemory()
        results = await mem.search("anything")
        assert results == []

    async def test_case_insensitive_search(self):
        mem = KeywordMemory()
        await mem.add("PYTHON is FUN")
        results = await mem.search("python")
        assert len(results) == 1
