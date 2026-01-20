"""Streaming utilities."""
from typing import AsyncIterator, Iterator
import asyncio


async def stream_to_async(iterator: Iterator) -> AsyncIterator:
    """Convert sync iterator to async iterator.
    
    Args:
        iterator: Synchronous iterator
        
    Yields:
        Items from iterator
    """
    for item in iterator:
        yield item
        await asyncio.sleep(0)  # Allow other tasks to run


class StreamBuffer:
    """Buffer for streaming data."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize stream buffer.
        
        Args:
            max_size: Maximum buffer size
        """
        self.buffer = []
        self.max_size = max_size
    
    def add(self, chunk: str):
        """Add chunk to buffer."""
        self.buffer.append(chunk)
        
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size:]
    
    def get_all(self) -> str:
        """Get all buffered content."""
        return "".join(self.buffer)
    
    def clear(self):
        """Clear buffer."""
        self.buffer.clear()
