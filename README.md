# Production AI Agent System

A **production-grade conversational AI agent system** with LLM integration, tool execution, and stateful conversation management.

## Features

- **Core Agent Framework**: Production-ready agent with conversation management and memory
- **LLM Integration**: Google Gemini with async support, streaming, and retry logic
- **Tool System**: Extensible tool framework with built-in tools (code execution, file ops, data analysis)
- **E2B Sandboxes**: Secure cloud execution environments for code
- **Conversation Memory**: Persistent conversation history and context
- **Error Handling**: Retry logic with exponential backoff
- **Observability**: Structured logging and metrics

## Architecture

```
orchestrator/
├── core/
│   ├── agent.py          # Main agent class
│   ├── conversation.py   # Conversation management
│   └── memory.py         # Memory store
├── providers/
│   ├── gemini.py        # Google Gemini integration
│   └── e2b.py           # E2B sandbox provider
├── tools/
│   ├── base.py          # Tool interface
│   ├── registry.py      # Tool registry
│   ├── executor.py      # Tool execution
│   └── implementations.py # Built-in tools
└── utils/
    ├── logging.py       # Logging utilities
    ├── retry.py         # Retry logic
    └── streaming.py     # Streaming support
```

## Quick Start

### 1. Install Dependencies

```bash
# Using uv pip (recommended)
uv pip install -r requirements.txt

# Or using the setup script
./setup.sh
```

### 2. Get API Keys

**Gemini API Key** (FREE):
- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Sign in and create an API key
- Gemini is free for moderate usage

**E2B API Key**:
- Visit [E2B](https://e2b.dev)
- Sign up and get your API key

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your keys:
# GEMINI_API_KEY=your_gemini_key_here
# E2B_API_KEY=your_e2b_key_here
```

### 4. Verify Installation

```bash
python verify.py
```

All checks should pass. If any fail, ensure dependencies are installed.

### 5. Run Example

```bash
# Interactive conversation
python main.py

# Run predefined tasks
python main.py tasks
```

## Example Usage

```python
from orchestrator.core.agent import Agent, AgentConfig
from orchestrator.providers.gemini import GeminiProvider
from orchestrator.providers.e2b import E2BProvider
from orchestrator.tools.executor import ToolExecutor

# Configure agent
config = AgentConfig(
    name="MyAgent",
    model="gemini-2.0-flash-exp",
    tools_enabled=True,
    system_prompt="You are a helpful assistant..."
)

# Initialize providers
llm = GeminiProvider()
e2b = E2BProvider()
tools = ToolExecutor(e2b)

# Create agent
agent = Agent(config, llm, tools)

# Run
response = await agent.run(
    message="Analyze data.csv and create a visualization",
    session_id="session-123"
)

print(response.content)
```

See [docs/e2b_guide.md](docs/e2b_guide.md) for E2B setup and [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

## Documentation

- **[Architecture](docs/architecture.md)** - System design and flow
- **[E2B Guide](docs/e2b_guide.md)** - Setup and configuration  
- **[E2B Examples](docs/e2b_examples.md)** - Code examples

## Structure

- `docker/` - Sandbox environment images
- `registry/` - Declarative configs (NO logic)
- `orchestrator/` - Session and sandbox lifecycle management
- `api/` - Control surface for external systems
- `storage/` - Persistent storage (OUTSIDE sandbox)
- `sandbox_runtime/` - Execution environment (INSIDE sandbox)
- `docs/` - Documentation
- `pyproject.toml` - Package configuration (UV)
