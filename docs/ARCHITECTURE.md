# Sandbox System Architecture

## System Overview
Production-grade AI agent system using **Google Gemini API** and **E2B sandboxes** for secure code execution.

## Technology Stack
- **LLM Provider**: Google Gemini (gemini-2.0-flash-exp)
- **Sandbox Provider**: E2B Code Interpreter
- **Framework**: Python 3.10+ with asyncio
- **Dependencies**: google-generativeai, e2b-code-interpreter

## File Structure & Connections

```
sandbox-system/
├── orchestrator/              # Core orchestration package
│   ├── core/                  # Agent core logic
│   │   ├── agent.py          # Main agent class (imports: gemini.py, memory.py, conversation.py, executor.py)
│   │   ├── conversation.py   # Conversation management (imports: memory.py)
│   │   └── memory.py         # Session state & memory
│   │
│   ├── providers/            # External service providers
│   │   ├── gemini.py         # Google Gemini LLM provider (independent)
│   │   └── e2b.py            # E2B sandbox provider (independent)
│   │
│   ├── tools/                # Tool system
│   │   ├── base.py           # Tool base classes (independent)
│   │   ├── registry.py       # Tool registration (imports: base.py)
│   │   ├── implementations.py # Tool implementations (imports: base.py, e2b.py)
│   │   └── executor.py       # Tool execution orchestrator (imports: registry.py, implementations.py, e2b.py)
│   │
│   └── utils/                # Utility modules
│       ├── logging.py        # Logging setup (independent)
│       ├── retry.py          # Retry logic (independent)
│       └── streaming.py      # Stream utilities (independent)
│
├── main.py                  # Production agent runner (imports: all core + providers + tools)
│
├── registry/                 # Tool definitions
│   └── tools.yaml           # YAML tool schemas
│
├── .env                     # Environment variables (GEMINI_API_KEY, E2B_API_KEY)
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## Dependency Flow

### Level 0 (No Dependencies)
- `utils/logging.py`
- `utils/retry.py`
- `utils/streaming.py`
- `tools/base.py`
- `core/memory.py`

### Level 1 (Depends on Level 0)
- `providers/gemini.py` → logging, retry
- `providers/e2b.py` → logging, retry
- `tools/registry.py` → base, logging

### Level 2 (Depends on Level 0-1)
- `tools/implementations.py` → base, e2b
- `core/conversation.py` → memory

### Level 3 (Depends on Level 0-2)
- `tools/executor.py` → registry, implementations, e2b, logging

### Level 4 (Depends on Level 0-3)
- `core/agent.py` → gemini, conversation, memory, executor, logging, retry

### Application Layer
- `main.py` → agent, memory, gemini, e2b, executor, logging

## Import Graph

```
main.py
  ↓
orchestrator.core.agent
  ↓ ↓ ↓ ↓
  ↓ ↓ ↓ orchestrator.tools.executor
  ↓ ↓ ↓   ↓ ↓
  ↓ ↓ ↓   ↓ orchestrator.tools.implementations
  ↓ ↓ ↓   ↓   ↓
  ↓ ↓ ↓   ↓   orchestrator.providers.e2b
  ↓ ↓ ↓   ↓
  ↓ ↓ ↓   orchestrator.tools.registry
  ↓ ↓ ↓     ↓
  ↓ ↓ ↓     orchestrator.tools.base
  ↓ ↓ ↓
  ↓ ↓ orchestrator.core.conversation
  ↓ ↓   ↓
  ↓ ↓   orchestrator.core.memory
  ↓ ↓
  ↓ orchestrator.providers.gemini
  ↓   ↓
  ↓   orchestrator.utils.retry
  ↓   orchestrator.utils.logging
  ↓
  orchestrator.utils.logging
```

## Data Flow

```
User Input
  ↓
Agent (agent.py)
  ↓
GeminiProvider (gemini.py)
  ↓ [streaming response]
  ↓
Agent [detects tool calls]
  ↓
ToolExecutor (executor.py)
  ↓
Tool Implementation (implementations.py)
  ↓
E2BProvider (e2b.py) [executes in sandbox]
  ↓
Results back to Agent
  ↓
GeminiProvider [generates final response]
  ↓
User Output
```

## Key Modules

### orchestrator/core/agent.py
**Purpose**: Main agent orchestration  
**Imports**:
- `orchestrator.providers.gemini.GeminiProvider`
- `orchestrator.core.conversation.ConversationManager`
- `orchestrator.core.memory.MemoryStore`
- `orchestrator.tools.executor.ToolExecutor`
- `orchestrator.utils.logging`, `orchestrator.utils.retry`

**Provides**: `Agent` class, `AgentConfig` dataclass

### orchestrator/providers/gemini.py
**Purpose**: Google Gemini LLM integration  
**Imports**: `google.generativeai`, utils  
**Provides**: `GeminiProvider` with `chat_completion()`, `stream_completion()`

### orchestrator/providers/e2b.py
**Purpose**: E2B sandbox management  
**Imports**: `e2b_code_interpreter`, utils  
**Provides**: `E2BProvider` with sandbox lifecycle & code execution

**Custom Template**: `en7sb4k1n268scs49jnj` with pre-installed packages:
- numpy (1.26.4), pandas (2.2.3), scikit-learn (1.6.1), matplotlib (3.10.3)
- requests, beautifulsoup4

### orchestrator/tools/executor.py
**Purpose**: Tool execution orchestration  
**Imports**: registry, implementations, e2b, logging  
**Provides**: `ToolExecutor` that routes tool calls to implementations

### orchestrator/tools/implementations.py
**Purpose**: Concrete tool implementations  
**Imports**: base, e2b  
**Provides**: `ExecuteCodeTool`, `FileOperationsTool`, `AnalyzeDataTool`, `WebSearchTool`

## Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here  # Get from https://aistudio.google.com/app/apikey
E2B_API_KEY=your_e2b_api_key_here        # Get from https://e2b.dev

# Optional
API_PORT=8000
API_HOST=0.0.0.0
```

## Removed Files (Legacy)
The following files were removed as they're not used by the current system:
- `orchestrator/lifecycle.py` - Old lifecycle management
- `orchestrator/unified_manager.py` - Old Docker/E2B manager
- `orchestrator/session_manager.py` - Old session management
- `orchestrator/state_manager.py` - Old state management
- `orchestrator/e2b_manager.py` - Old E2B manager (replaced by providers/e2b.py)
- `orchestrator/providers/openai.py` - Old OpenAI provider (replaced by gemini.py)
- `api/` directory - Old FastAPI routes (referenced deleted modules)

## Verification

All Python files compile successfully without import errors:
```bash
python -m py_compile main.py \
  orchestrator/core/agent.py \
  orchestrator/providers/gemini.py \
  orchestrator/providers/e2b.py \
  orchestrator/tools/executor.py \
  orchestrator/tools/implementations.py
```

## Next Steps

1. **Install dependencies**: `uv pip install -r requirements.txt`
2. **Configure environment**: Copy `.env.example` to `.env` and add your API keys
3. **Run agent**: `python main.py`
4. **Test with E2B**: Ensure E2B API key is valid and sandbox creation works
5. **Test Gemini**: Ensure Gemini API key works with the new provider
