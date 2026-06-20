"""Example: adding a custom tool to the agent."""
import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv

from orchestrator import Agent, AgentConfig, GeminiProvider, E2BProvider, ToolExecutor, ToolRegistry, BaseTool

load_dotenv()


class WeatherTool(BaseTool):
    """Example custom tool - in production this would call a real weather API."""

    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get the current weather for a city",
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name",
                        }
                    },
                    "required": ["city"],
                },
            },
        }

    async def execute(self, session_id: str, city: str, **kwargs) -> Dict[str, Any]:
        return {
            "success": True,
            "city": city,
            "temperature": 22,
            "conditions": "sunny",
            "humidity": 45,
        }


async def main():
    registry = ToolRegistry()
    registry.register(WeatherTool())

    executor = ToolExecutor(
        e2b_provider=E2BProvider(),
        registry=registry,
    )

    config = AgentConfig(
        name="CustomToolAgent",
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        system_prompt="You have access to a weather tool. Answer user questions about weather.",
        tools_enabled=True,
    )

    agent = Agent(
        config=config,
        llm_provider=GeminiProvider(),
        tool_executor=executor,
    )

    async with agent:
        response = await agent.run("What's the weather in Tokyo?", session_id="weather-demo")
        print(f"Response: {response.content}")


asyncio.run(main())
