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
make verify
# or: python scripts/verify.py
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

See [docs/e2b_guide.md](docs/e2b_guide.md) for E2B setup and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design.

## Quick Commands

```bash
make run              # Start conversational agent
make verify           # Verify all imports
make map              # Generate connection map
make list-models      # List available Gemini models
make cleanup-sandboxes # Clean up E2B sandboxes
make clean            # Clean Python cache files
```

## Project Structure

```
sandbox-system/
├── main.py                     # Main conversational agent
├── scripts/                    # Utility scripts
│   ├── cleanup_sandboxes.py   # E2B sandbox cleanup
│   ├── list_models.py         # List Gemini models
│   ├── verify.py              # Import verification
│   └── map_connections.py     # Connection mapper
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # System architecture
│   └── e2b_guide.md          # E2B integration guide
├── orchestrator/              # Core system
│   ├── core/                  # Agent engine
│   ├── providers/             # Gemini + E2B providers
│   ├── tools/                 # Tool execution
│   └── utils/                 # Utilities
├── registry/tools/            # Tool definitions (YAML)
├── storage/                   # Persistent storage
├── requirements.txt           # Dependencies
├── pyproject.toml            # Package config
├── Makefile                  # Quick commands
└── .env                      # API keys (not committed)
```

## Documentation

- **[ARCHITECTURE](docs/ARCHITECTURE.md)** - System design and architecture
- **[E2B Guide](docs/e2b_guide.md)** - E2B integration details

## Migration

This system was migrated to Google Gemini. All code has been updated:
- ✅ Full Gemini API integration (google-genai>=1.0.0)
- ✅ E2B Code Interpreter 1.0.0
- ✅ Tool calling and function execution
- ✅ Sandbox lifecycle management
- ✅ Production-ready error handling
