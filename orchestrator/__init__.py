"""sandbox-system: AI Agent System with Gemini and E2B Sandboxes.

A production-grade library for building AI agents that can execute code
in secure cloud sandboxes. Provides conversation management, tool execution,
memory persistence, and pluggable LLM providers.

Typical usage:

    from orchestrator import Agent, AgentConfig, GeminiProvider, E2BProvider

    config = AgentConfig(name="my-agent", system_prompt="You are helpful")
    agent = Agent(
        config=config,
        llm_provider=GeminiProvider(),
        tool_executor=ToolExecutor(e2b_provider=E2BProvider())
    )

    response = await agent.run("Hello!", session_id="session-1")
    print(response.content)
"""

from orchestrator.core.agent import Agent, AgentConfig, AgentResponse
from orchestrator.core.memory import MemoryStore, KeywordMemory
from orchestrator.providers.gemini import GeminiProvider
from orchestrator.providers.e2b import E2BProvider
from orchestrator.tools.executor import ToolExecutor
from orchestrator.tools.registry import ToolRegistry
from orchestrator.tools.base import BaseTool

__all__ = [
    "Agent",
    "AgentConfig",
    "AgentResponse",
    "MemoryStore",
    "KeywordMemory",
    "GeminiProvider",
    "E2BProvider",
    "ToolExecutor",
    "ToolRegistry",
    "BaseTool",
]
