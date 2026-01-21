"""Memory and context storage for agents."""
import json
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta


class MemoryStore:
    """In-memory store with optional file persistence."""
    
    def __init__(self, storage_dir: Optional[str] = "./storage/memory"):
        """Initialize memory store.
        
        Args:
            storage_dir: Directory for persistent storage
        """
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self.cache: Dict[str, Any] = {}
        self.ttl: Dict[str, datetime] = {}
        
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from memory.
        
        Args:
            key: Memory key
            default: Default value if not found
            
        Returns:
            Stored value or default
        """
        # Check TTL
        if key in self.ttl and datetime.utcnow() > self.ttl[key]:
            await self.delete(key)
            return default
        
        return self.cache.get(key, default)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ):
        """Set value in memory.
        
        Args:
            key: Memory key
            value: Value to store
            ttl_seconds: Time to live in seconds
        """
        self.cache[key] = value
        
        if ttl_seconds:
            self.ttl[key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        if self.storage_dir:
            await self._persist_to_disk(key, value)
    
    async def delete(self, key: str):
        """Delete value from memory."""
        self.cache.pop(key, None)
        self.ttl.pop(key, None)
        
        if self.storage_dir:
            file_path = self.storage_dir / f"{self._safe_key(key)}.json"
            if file_path.exists():
                file_path.unlink()
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)
        return value is not None
    
    async def keys(self, pattern: Optional[str] = None) -> list:
        """Get all keys, optionally filtered by pattern.
        
        Args:
            pattern: Optional pattern to filter keys
            
        Returns:
            List of matching keys
        """
        keys = list(self.cache.keys())
        
        if pattern:
            keys = [k for k in keys if pattern in k]
        
        return keys
    
    async def clear(self):
        """Clear all memory."""
        self.cache.clear()
        self.ttl.clear()
        
        if self.storage_dir:
            for file in self.storage_dir.glob("*.json"):
                file.unlink()
    
    def _safe_key(self, key: str) -> str:
        """Convert key to safe filename."""
        return key.replace(":", "_").replace("/", "_").replace(" ", "_")
    
    def _load_from_disk(self):
        """Load persisted memory from disk."""
        if not self.storage_dir:
            return
        
        for file in self.storage_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    # Restore original key from filename
                    key = file.stem.replace("_", ":")
                    self.cache[key] = data
            except Exception:
                pass  # Skip corrupted files
    
    async def _persist_to_disk(self, key: str, value: Any):
        """Persist value to disk."""
        if not self.storage_dir:
            return
        
        file_path = self.storage_dir / f"{self._safe_key(key)}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(value, f, indent=2, default=str)
        except Exception as e:
            # Log error but don't fail
            print(f"Failed to persist {key}: {e}")


class VectorMemory:
    """Vector-based semantic memory (placeholder for future embedding support)."""
    
    def __init__(self):
        """Initialize vector memory."""
        self.documents = []
    
    async def add(self, text: str, metadata: Optional[Dict] = None):
        """Add document to vector memory."""
        self.documents.append({
            "text": text,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def search(self, query: str, limit: int = 5) -> list:
        """Search for similar documents.
        
        Note: This is a placeholder. In production, use embeddings.
        """
        # Simple keyword search for now
        results = []
        for doc in self.documents:
            if any(word.lower() in doc["text"].lower() for word in query.split()):
                results.append(doc)
                if len(results) >= limit:
                    break
        
        return results
