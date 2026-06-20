"""Quickstart: using the sandbox-system as a library.

    uv sync
    cp .env.example .env   # add your API keys
    python examples/quickstart.py
"""
import asyncio
import os
from dotenv import load_dotenv

from orchestrator import Agent, AgentConfig, GeminiProvider, E2BProvider, ToolExecutor

load_dotenv()

SYSTEM_PROMPT = """You are a helpful AI assistant.
Use tools to answer questions and solve problems."""


async def main():
    config = AgentConfig(
        name="QuickstartAgent",
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        system_prompt=SYSTEM_PROMPT,
        tools_enabled=True,
        max_iterations=10,
    )

    agent = Agent(
        config=config,
        llm_provider=GeminiProvider(),
        tool_executor=ToolExecutor(
            e2b_provider=E2BProvider(),
        ),
    )

    async with agent:
        response = await agent.run("What is 15 * 37?", session_id="quickstart")
        print(f"Answer: {response.content}")

        response = await agent.run(
            "Use Python to verify: write code to compute 15 * 37",
            session_id="quickstart",
        )
        print(f"With verification: {response.content}")


asyncio.run(main())
