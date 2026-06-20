# Sandbox AI Agent System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-100%25-passing)](tests/)
[![Ruff](https://img.shields.io/badge/Lint-Ruff-success)](https://github.com/astral-sh/ruff)

A production-grade Python library for building AI agents that execute code in secure cloud sandboxes. Combines Google Gemini for reasoning with E2B sandboxes for safe, isolated code execution.

**What makes this different?** LLMs hallucinate code — this agent actually runs it. When Gemini generates Python, it executes in a real sandbox, gets real results, and iterates on real errors. The `orchestrator` package provides the reusable framework; `main.py` is just a demo.

---

## Architecture

```
                    ┌──────────────────────────────────┐
                    │            Agent                  │
                    │  (conversation loop, tool loop)   │
                    └──────┬──────────────┬─────────────┘
                           │              │
                    ┌──────┴──────┐ ┌─────┴──────────┐
                    │  Gemini     │ │  ToolExecutor   │
                    │  Provider   │ │  (routes tools) │
                    └─────────────┘ └──┬────┬────┬────┘
                                       │    │    │
                              ┌────────┘    │    └────────┐
                              │             │              │
                    ┌─────────┴──┐  ┌───────┴──────┐  ┌───┴──────────┐
                    │  E2B       │  │  WebSearch   │  │  DataAnalysis │
                    │  Sandbox   │  │  Tool        │  │  Tool         │
                    └────────────┘  └──────────────┘  └──────────────┘
```

**Core loop:**
1. User message → Agent loads conversation history (+ system prompt)
2. Messages sent to Gemini → returns text or tool calls
3. Tool calls dispatched to `ToolExecutor` → results fed back to Gemini
4. Loop continues until Gemini responds with text (or max iterations reached)
5. Response saved to conversation memory + returned to caller

---

## Library API (the real product)

```python
from orchestrator import Agent, AgentConfig, GeminiProvider, E2BProvider, ToolExecutor

config = AgentConfig(
    name="my-agent",
    model="gemini-2.0-flash-exp",
    system_prompt="You are a helpful assistant with sandboxed Python execution.",
    tools_enabled=True,
)

async with Agent(
    config=config,
    llm_provider=GeminiProvider(),
    tool_executor=ToolExecutor(e2b_provider=E2BProvider()),
) as agent:
    response = await agent.run("Compute 15 * 37 using Python", session_id="demo")
    print(response.content)
```

More examples in [`examples/`](examples/):
- [`quickstart.py`](examples/quickstart.py) — minimal working example
- [`custom_tool.py`](examples/custom_tool.py) — adding a `WeatherTool`
- [`multi_turn.py`](examples/multi_turn.py) — conversation with memory + reset

---

## Quickstart (CLI demo)

```bash
uv sync
cp .env.example .env          # add GEMINI_API_KEY and E2B_API_KEY

python main.py                # interactive chat
python main.py tasks          # run 3 demo data-analysis tasks
```

---

## API Reference

### `Agent`
The central orchestrator. Maintains conversation state, calls the LLM, executes tools, and manages the agent loop.

```python
agent = Agent(config, llm_provider, tool_executor, memory_store)

response = await agent.run(message="...", session_id="s1")
# response.content  → final text
# response.tool_calls → tools invoked
# response.artifacts → generated images/charts
# response.metadata  → iteration count, usage stats

await agent.reset_session("s1")   # clear conversation history

async with agent as a:            # context manager cleans up sandboxes
    ...
```

### `AgentConfig`
```python
AgentConfig(
    name: str,                          # agent identifier
    model: str = "gemini-2.0-flash-exp", # Gemini model
    temperature: float = 0.7,
    system_prompt: str | None = None,
    tools_enabled: bool = True,
    max_iterations: int = 10,
    streaming: bool = False,
)
```

### `ToolExecutor`
Routes tool calls to registered tool implementations. Built-in tools:
- `execute_code` — run Python in E2B sandbox (numpy, pandas, matplotlib, sklearn)
- `file_operations` — read/write/list files in sandbox
- `analyze_data` — CSV/Excel summary stats and visualizations
- `web_search` — DuckDuckGo search (no API key needed)

### Extending with custom tools

```python
from orchestrator import BaseTool, ToolRegistry

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(name="my_tool", description="Does something useful")

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": { ... },
            },
        }

    async def execute(self, session_id: str, **kwargs) -> dict:
        return {"success": True, "result": ...}

# Register and use
registry = ToolRegistry()
registry.register(MyTool())
executor = ToolExecutor(e2b_provider=E2BProvider(), registry=registry)
```

### `MemoryStore` & `ConversationManager`
- `MemoryStore` — persistent key-value storage on disk (JSON-based)
- `KeywordMemory` — in-memory keyword-indexed search
- `ConversationManager` — manages message history per session with size limits and path-traversal protection

---

## Testing

```bash
pytest tests/ -v     # 100 tests
ruff check .          # zero lint errors
```

Test coverage includes agent loop, tool execution, sandbox lifecycle, memory persistence, conversation security, and provider initialization.

---

## Project Structure

```
sandbox-system/
├── orchestrator/          # 📦 Reusable library (uv-installable)
│   ├── core/              # Agent, conversation, memory
│   ├── providers/         # Gemini LLM, E2B sandbox
│   ├── tools/             # Base tool, registry, executor, implementations
│   └── utils/             # Logging, retry logic
├── main.py                # 🎮 CLI demo (not the product)
├── examples/              # 📖 Library usage examples
├── tests/                 # 🧪 100 tests
└── .env.example           # 🔑 Required: GEMINI_API_KEY + E2B_API_KEY
```

---

## Why this exists

LLMs are great at generating code but can't run it. This system bridges that gap:

- **Security**: code executes in E2B's isolated cloud sandboxes, not on the host
- **Correctness**: the agent sees actual stdout/stderr and iterates on real errors
- **Data**: generates real charts and files, not markdown approximations
- **Memory**: persists conversation context across turns for multi-step workflows

Built for developers who need AI agents that can *do* things, not just *say* things.
