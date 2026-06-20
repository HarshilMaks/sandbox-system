"""Example: multi-turn conversation with memory."""
import asyncio
import os
from dotenv import load_dotenv

from orchestrator import Agent, AgentConfig, GeminiProvider, E2BProvider, ToolExecutor

load_dotenv()

SYSTEM_PROMPT = """You are a helpful AI assistant.
You remember previous context and can build on earlier conversations."""


async def main():
    config = AgentConfig(
        name="ConversationAgent",
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        system_prompt=SYSTEM_PROMPT,
        tools_enabled=True,
    )

    agent = Agent(
        config=config,
        llm_provider=GeminiProvider(),
        tool_executor=ToolExecutor(e2b_provider=E2BProvider()),
    )

    session = "multi-turn-demo"

    async with agent:
        response = await agent.run("My name is Alice", session_id=session)
        print(f"Turn 1: {response.content}\n")

        response = await agent.run("What is my name?", session_id=session)
        print(f"Turn 2: {response.content}\n")

        response = await agent.run(
            "Write a Python script that greets me by name", session_id=session
        )
        print(f"Turn 3: {response.content}\n")

        await agent.reset_session(session)
        response = await agent.run("What is my name?", session_id=session)
        print(f"Turn 4 (after reset): {response.content}")


asyncio.run(main())
