"""Production-grade conversational AI agent example."""
import os
import asyncio
import base64
from pathlib import Path

from dotenv import load_dotenv

from orchestrator.core.agent import Agent, AgentConfig
from orchestrator.core.memory import MemoryStore
from orchestrator.providers.gemini import GeminiProvider
from orchestrator.providers.e2b import E2BProvider
from orchestrator.tools.executor import ToolExecutor
from orchestrator.utils.logging import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level=log_level, log_file="./logs/agent.log")
logger = get_logger("example.conversational_agent")


SYSTEM_PROMPT = """You are a helpful AI assistant with access to powerful tools:

1. **execute_code**: Run Python code in a secure sandbox
   - Use for calculations, data processing, file manipulation
   - Has access to pandas, numpy, matplotlib, scikit-learn

2. **file_operations**: Read, write, list files in the sandbox
   - Use to store data, load files, manage workspace

3. **analyze_data**: Analyze CSV/Excel files
   - Get summary statistics, visualizations, correlations

4. **web_search**: Search the web for current information, news, and data
   - Uses DuckDuckGo (no API key needed)

Guidelines:
- Always break complex tasks into steps
- Use tools when needed - don't try to compute things yourself
- Show your work and explain your reasoning
- Handle errors gracefully and suggest alternatives
- When analyzing data, start with summary before detailed analysis

You maintain conversation context and remember previous interactions.
"""


def save_artifacts(artifacts: list, output_dir: Path, session_id: str) -> list:
    """Save generated artifacts (images, etc.) to disk.
    
    Returns:
        List of saved file paths.
    """
    saved = []
    for i, artifact in enumerate(artifacts):
        if artifact.get("type") == "image/png" and artifact.get("data"):
            filename = f"{session_id}_artifact_{i}.png"
            filepath = output_dir / filename
            try:
                data = artifact["data"]
                if isinstance(data, str):
                    data = base64.b64decode(data)
                filepath.write_bytes(data)
                saved.append(str(filepath))
            except Exception as e:
                logger.warning(f"Failed to save artifact {i}: {e}")
    return saved


async def run_conversation_agent():
    """Run interactive conversational agent."""
    
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    logger.info(f"Initializing conversational agent (model={model})...")
    
    # Initialize providers & tools
    gemini_provider = GeminiProvider(
        api_key=os.getenv("GEMINI_API_KEY"),
        model=model
    )
    e2b_provider = E2BProvider(api_key=os.getenv("E2B_API_KEY"))
    tool_executor = ToolExecutor(e2b_provider=e2b_provider)
    memory_store = MemoryStore(storage_dir="./storage/memory")
    output_dir = Path("./output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = AgentConfig(
        name="ConversationalAgent",
        model=model,
        temperature=0.7,
        system_prompt=SYSTEM_PROMPT,
        tools_enabled=True,
        max_iterations=10
    )
    
    agent = Agent(
        config=config,
        llm_provider=gemini_provider,
        tool_executor=tool_executor,
        memory_store=memory_store
    )
    
    session_id = "demo-session-001"
    logger.info(f"Creating E2B sandbox for session {session_id}")
    e2b_provider.create_sandbox(session_id)
    
    print("\n" + "="*60)
    print("SANDBOX AI AGENT - Interactive Mode")
    print("="*60)
    print("Type 'quit' to exit, 'reset' to clear history\n")
    
    try:
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == "quit":
                break
            
            if user_input.lower() == "reset":
                await agent.reset_session(session_id)
                print("✓ Session reset\n")
                continue
            
            if not user_input:
                continue
            
            print()
            response = await agent.run(
                message=user_input,
                session_id=session_id
            )
            
            if response.content:
                print(response.content)
            
            # Save & report artifacts
            saved = save_artifacts(response.artifacts, output_dir, session_id)
            if saved:
                print("\n📁 Generated files:")
                for path in saved:
                    print(f"   {path}")
            
            # Show metadata
            info = []
            if response.tool_calls:
                info.append(f"{len(response.tool_calls)} tool(s) used")
            if response.metadata.get("iterations"):
                info.append(f"{response.metadata['iterations']} iteration(s)")
            if response.usage:
                info.append(f"{response.usage.get('total_tokens', '?')} tokens")
            if info:
                print(f"\n[{', '.join(info)}]")
    
    finally:
        logger.info("Cleaning up...")
        e2b_provider.close_sandbox(session_id)
        print("\n✓ Session ended")


async def run_example_tasks():
    """Run predefined example tasks demonstrating the sandbox system."""
    
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    logger.info(f"Running example tasks (model={model})...")
    
    gemini_provider = GeminiProvider(
        api_key=os.getenv("GEMINI_API_KEY"),
        model=model
    )
    e2b_provider = E2BProvider(api_key=os.getenv("E2B_API_KEY"))
    tool_executor = ToolExecutor(e2b_provider=e2b_provider)
    memory_store = MemoryStore(storage_dir="./storage/memory")
    output_dir = Path("./output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = AgentConfig(
        name="TaskAgent",
        model=model,
        temperature=0.7,
        system_prompt=SYSTEM_PROMPT,
        tools_enabled=True,
        max_iterations=10
    )
    
    agent = Agent(
        config=config,
        llm_provider=gemini_provider,
        tool_executor=tool_executor,
        memory_store=memory_store
    )
    
    session_id = "task-session-001"
    e2b_provider.create_sandbox(session_id)
    
    tasks = [
        "Generate a CSV file with 100 random data points (x, y coordinates) and save it to /data/points.csv",
        "Analyze the data file I just created and show me summary statistics",
        "Create a scatter plot of the data and tell me if there's any pattern"
    ]
    
    print("\n" + "="*60)
    print("SANDBOX AI AGENT - Example Tasks")
    print("="*60)
    
    try:
        for i, task in enumerate(tasks, 1):
            print(f"\n{'─'*60}")
            print(f"TASK {i}: {task}")
            print(f"{'─'*60}")
            
            response = await agent.run(
                message=task,
                session_id=session_id
            )
            
            if response.content:
                print(f"\n{response.content}")
            
            saved = save_artifacts(response.artifacts, output_dir, session_id)
            if saved:
                print("\n📁 Generated files:")
                for path in saved:
                    print(f"   {path}")
            
            info = []
            if response.tool_calls:
                info.append(f"{len(response.tool_calls)} tool(s) used")
            if response.usage:
                info.append(f"{response.usage.get('total_tokens', '?')} tokens")
            if info:
                print(f"[{', '.join(info)}]")
    
    finally:
        e2b_provider.close_sandbox(session_id)
        print("\n✓ All tasks completed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "tasks":
        asyncio.run(run_example_tasks())
    else:
        asyncio.run(run_conversation_agent())
