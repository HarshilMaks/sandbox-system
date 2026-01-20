"""Conversation management with history and context."""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from orchestrator.core.memory import MemoryStore


class ConversationManager:
    """Manages conversation history and context."""
    
    def __init__(self, memory_store: MemoryStore, max_history: int = 50):
        """Initialize conversation manager.
        
        Args:
            memory_store: Memory storage backend
            max_history: Maximum messages to keep per session
        """
        self.memory = memory_store
        self.max_history = max_history
    
    async def get_messages(self, session_id: str) -> List[Dict]:
        """Get conversation messages for session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages in OpenAI format
        """
        history = await self.memory.get(f"conversation:{session_id}", [])
        
        # Return last N messages
        return history[-self.max_history:]
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add message to conversation.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system, tool)
            content: Message content
            metadata: Additional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        history = await self.memory.get(f"conversation:{session_id}", [])
        history.append(message)
        
        # Keep only recent messages
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        await self.memory.set(f"conversation:{session_id}", history)
    
    async def get_context(self, session_id: str, window: int = 5) -> str:
        """Get recent conversation context as string.
        
        Args:
            session_id: Session identifier
            window: Number of recent messages to include
            
        Returns:
            Formatted context string
        """
        messages = await self.get_messages(session_id)
        recent = messages[-window:]
        
        context_parts = []
        for msg in recent:
            role = msg["role"].capitalize()
            content = msg["content"][:200]  # Truncate long messages
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    async def clear_session(self, session_id: str):
        """Clear conversation history for session."""
        await self.memory.delete(f"conversation:{session_id}")
    
    async def get_summary(self, session_id: str) -> Dict:
        """Get conversation summary statistics.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Summary dict with message counts, duration, etc.
        """
        messages = await self.get_messages(session_id)
        
        if not messages:
            return {"message_count": 0}
        
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        first_msg = messages[0]
        last_msg = messages[-1]
        
        duration = None
        if "timestamp" in first_msg and "timestamp" in last_msg:
            start = datetime.fromisoformat(first_msg["timestamp"])
            end = datetime.fromisoformat(last_msg["timestamp"])
            duration = (end - start).total_seconds()
        
        return {
            "message_count": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "duration_seconds": duration,
            "first_message_at": first_msg.get("timestamp"),
            "last_message_at": last_msg.get("timestamp")
        }
