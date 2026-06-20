"""Core agent framework for production AI systems."""
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json

from orchestrator.core.conversation import ConversationManager
from orchestrator.core.memory import MemoryStore
from orchestrator.providers.gemini import GeminiProvider
from orchestrator.tools.executor import ToolExecutor
from orchestrator.utils.logging import get_logger
from orchestrator.utils.retry import with_retry


@dataclass
class AgentConfig:
    """Agent configuration."""
    name: str
    model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    tools_enabled: bool = True
    streaming: bool = False
    max_iterations: int = 10
    timeout: int = 300


@dataclass
class AgentResponse:
    """Agent response."""
    content: str
    tool_calls: List[Dict] = field(default_factory=list)
    artifacts: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage: Optional[Dict] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Agent:
    """Production-grade AI agent with conversation management and tool execution."""
    
    def __init__(
        self,
        config: AgentConfig,
        llm_provider: Optional[GeminiProvider] = None,
        tool_executor: Optional[ToolExecutor] = None,
        memory_store: Optional[MemoryStore] = None
    ):
        """Initialize agent.
        
        Args:
            config: Agent configuration
            llm_provider: LLM provider (Gemini)
            tool_executor: Tool execution engine
            memory_store: Memory/context store
        """
        self.config = config
        self.logger = get_logger(f"agent.{config.name}")
        
        self.llm = llm_provider or GeminiProvider()
        self.tools = tool_executor
        self.memory = memory_store or MemoryStore()
        self.conversation = ConversationManager(self.memory)
        
        self.logger.info(f"Initialized agent: {config.name}")
    
    @with_retry(max_attempts=3, exponential_backoff=True)
    async def run(
        self,
        message: str,
        session_id: str,
        context: Optional[Dict] = None
    ) -> AgentResponse:
        """Run agent on a message.
        
        Args:
            message: User message
            session_id: Session identifier
            context: Additional context
            
        Returns:
            Agent response
        """
        self.logger.info(f"Processing message for session {session_id}")
        
        # Load conversation history
        messages = await self.conversation.get_messages(session_id)
        
        # Always insert system prompt (provider extracts it for Gemini)
        if self.config.system_prompt:
            messages.insert(0, {
                "role": "system",
                "content": self.config.system_prompt
            })
        
        # Add user message
        messages.append({"role": "user", "content": message})
        
        # Get tools if enabled
        tools = None
        if self.config.tools_enabled and self.tools:
            tools = self.tools.get_tool_schemas()
        
        # Execute agent loop
        iteration = 0
        content = ""
        all_artifacts = []
        while iteration < self.config.max_iterations:
            iteration += 1
            
            # Call LLM
            response = await self.llm.chat_completion(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=tools,
                stream=self.config.streaming
            )
            
            content = response.get("content") or ""
            
            # Add assistant message
            msg = {"role": "assistant", "content": content}
            if response.get("tool_calls"):
                msg["tool_calls"] = response["tool_calls"]
            messages.append(msg)
            
            # Check for tool calls
            if response.get("tool_calls"):
                self.logger.info(f"Executing {len(response['tool_calls'])} tool calls")
                
                for tool_call in response["tool_calls"]:
                    # Execute tool
                    result = await self.tools.execute(
                        session_id=session_id,
                        tool_name=tool_call["function"]["name"],
                        arguments=json.loads(tool_call["function"]["arguments"])
                    )
                    
                    # Collect artifacts from tool results
                    if result.get("artifacts"):
                        all_artifacts.extend(result["artifacts"])
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(result)
                    })
            else:
                break
        
        # Save user message to conversation history
        await self.conversation.add_message(
            session_id=session_id,
            role="user",
            content=message
        )
        
        # Save assistant response (skip empty tool-only responses)
        if content or response.get("tool_calls"):
            await self.conversation.add_message(
                session_id=session_id,
                role="assistant",
                content=content
            )
        
        return AgentResponse(
            content=content,
            tool_calls=response.get("tool_calls", []),
            artifacts=all_artifacts,
            metadata={"iterations": iteration},
            usage=response.get("usage")
        )
    
    async def stream(
        self,
        message: str,
        session_id: str
    ) -> AsyncIterator[str]:
        """Stream agent response.
        
        Args:
            message: User message
            session_id: Session identifier
            
        Yields:
            Response chunks
        """
        messages = await self.conversation.get_messages(session_id)
        
        if self.config.system_prompt:
            messages.insert(0, {
                "role": "system",
                "content": self.config.system_prompt
            })
        
        messages.append({"role": "user", "content": message})
        
        async for chunk in self.llm.stream_completion(
            messages=messages,
            model=self.config.model
        ):
            yield chunk
    
    async def reset_session(self, session_id: str):
        """Reset session conversation history."""
        await self.conversation.clear_session(session_id)
        self.logger.info(f"Reset session: {session_id}")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        if self.tools and hasattr(self.tools, "e2b_provider") and self.tools.e2b_provider:
            self.tools.e2b_provider.cleanup_all()
