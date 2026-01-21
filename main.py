"""Production-grade conversational AI agent example."""
import os
import asyncio

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
setup_logging(log_level="INFO", log_file="./logs/agent.log")
logger = get_logger("example.conversational_agent")


SYSTEM_PROMPT = """You are a helpful AI assistant with access to powerful tools:

1. **execute_code**: Run Python code in a secure sandbox
   - Use for calculations, data processing, file manipulation
   - Has access to pandas, numpy, matplotlib, scikit-learn

2. **file_operations**: Read, write, list files in the sandbox
   - Use to store data, load files, manage workspace

3. **analyze_data**: Analyze CSV/Excel files
   - Get summary statistics, visualizations, correlations

4. **web_search**: Search the web for information (placeholder)

Guidelines:
- Always break complex tasks into steps
- Use tools when needed - don't try to compute things yourself
- Show your work and explain your reasoning
- Handle errors gracefully and suggest alternatives
- When analyzing data, start with summary before detailed analysis

You maintain conversation context and remember previous interactions.
"""


async def run_conversation_agent():
    """Run interactive conversational agent."""
    
    logger.info("Initializing conversational agent...")
    
    # Initialize providers
    gemini_provider = GeminiProvider(
        api_key=os.getenv("GEMINI_API_KEY"),
        model=os.getenv("GEMINI_MODEL")
    )
    
    e2b_provider = E2BProvider(
        api_key=os.getenv("E2B_API_KEY")
    )
    
    # Create tool executor
    tool_executor = ToolExecutor(
        e2b_provider=e2b_provider,
        registry_path="./registry/tools"
    )
    
    # Create memory store
    memory_store = MemoryStore(storage_dir="./storage/memory")
    
    # Create agent
    config = AgentConfig(
        name="ConversationalAgent",
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
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
    
    # Session ID
    session_id = "demo-session-001"
    
    # Create sandbox for session
    logger.info(f"Creating E2B sandbox for session {session_id}")
    e2b_provider.create_sandbox(session_id)
    
    print("\n" + "="*60)
    print("CONVERSATIONAL AI AGENT")
    print("="*60)
    print("Type 'quit' to exit, 'reset' to clear history\n")
    
    try:
        while True:
            # Get user input
            user_input = input("\n You: ").strip()
            
            if user_input.lower() == "quit":
                break
            
            if user_input.lower() == "reset":
                await agent.reset_session(session_id)
                print("✓ Session reset")
                continue
            
            if not user_input:
                continue
            
            # Process message
            print("\nAssistant: ", end="", flush=True)
            
            response = await agent.run(
                message=user_input,
                session_id=session_id
            )
            
            print(response.content)
            
            # Show metadata
            if response.tool_calls:
                print(f"\n[Used {len(response.tool_calls)} tools in {response.metadata.get('iterations', 0)} iterations]")
            
            if response.usage:
                tokens = response.usage["total_tokens"]
                print(f"[Tokens: {tokens}]")
    
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        e2b_provider.close_sandbox(session_id)
        print("\n\n✓ Session ended")


async def run_example_tasks():
    """Run predefined example tasks."""
    
    logger.info("Running example tasks...")
    
    # Initialize
    gemini_provider = GeminiProvider()
    e2b_provider = E2BProvider()
    tool_executor = ToolExecutor(e2b_provider)
    memory_store = MemoryStore()
    
    config = AgentConfig(
        name="TaskAgent",
        model="gemini-2.0-flash-exp",
        system_prompt=SYSTEM_PROMPT,
        tools_enabled=True
    )
    
    agent = Agent(
        config=config,
        llm_provider=gemini_provider,
        tool_executor=tool_executor,
        memory_store=memory_store
    )
    
    session_id = "task-session-001"
    e2b_provider.create_sandbox(session_id)
    
    # Example tasks
    tasks = [
        "Generate a CSV file with 100 random data points (x, y coordinates) and save it to /data/points.csv",
        "Analyze the data file I just created and show me summary statistics",
        "Create a scatter plot of the data and tell me if there's any pattern"
    ]
    
    print("\n" + "="*60)
    print("RUNNING EXAMPLE TASKS")
    print("="*60)
    
    try:
        for i, task in enumerate(tasks, 1):
            print(f"\n\n{'='*60}")
            print(f"TASK {i}: {task}")
            print("="*60)
            
            response = await agent.run(
                message=task,
                session_id=session_id
            )
            
            print(f"\n🤖 Response:\n{response.content}")
            
            if response.tool_calls:
                print(f"\n[Tools used: {len(response.tool_calls)}]")
    
    finally:
        e2b_provider.close_sandbox(session_id)
        print("\n\n✓ All tasks completed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "tasks":
        # Run example tasks
        asyncio.run(run_example_tasks())
    else:
        # Run interactive conversation
        asyncio.run(run_conversation_agent())
