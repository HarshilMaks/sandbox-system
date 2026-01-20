# Architecture

## Overview
A **Stateful Sandbox System** for running AI agents in isolated, managed environments.

### Core Purpose
This system is NOT an agent framework. It is infrastructure for:
- Creating isolated execution environments
- Managing session lifecycle and state
- Executing code/tools safely
- Storing logs and artifacts
- Clean destruction of resources

Agent intelligence, reasoning, and orchestration happen OUTSIDE this system.

---

## System Flow

### Session Lifecycle

```
1. CREATE SESSION
   POST /api/sessions {"provider": "e2b", "environment": "Python3"}
   ↓
   SessionManager creates session ID
   ↓
   UnifiedSandboxManager starts E2B/Docker sandbox
   ↓
   Returns: {session_id, sandbox_id, provider, url}

2. EXECUTE CODE (E2B)
   POST /api/e2b/execute {"session_id": "...", "code": "..."}
   ↓
   E2BManager executes code
   ↓
   Returns: {stdout, stderr, results, artifacts}

3. MANAGE FILES (E2B)
   GET /api/e2b/files/{session_id}
   POST /api/e2b/files
   ↓
   File operations via E2B API

4. DESTROY SESSION
   DELETE /api/sessions/{session_id}
   ↓
   Stop sandbox
   ↓
   Clean up resources
```

---

## Components

### Registry (Declarative Configs)
YAML configs with NO logic:
- **environments/** - E2B templates (Python3, Node) or Docker images
- **agents/** - Agent capability definitions
- **tools/** - Tool specifications
- **prompts/** - System prompts

### Orchestrator (Business Logic)
Core system management:
- **unified_manager.py** - Multi-provider sandbox manager (Docker + E2B)
- **e2b_manager.py** - E2B-specific operations (code exec, files, network)
- **session_manager.py** - Session creation/destruction
- **state_manager.py** - State persistence (JSON files)
- **lifecycle.py** - High-level orchestration

### API (REST Interface)
Control surface:
- **POST /api/sessions** - Create session (specify provider)
- **DELETE /api/sessions/{id}** - Destroy session
- **GET /api/sessions/{id}** - Get session state
- **POST /api/e2b/execute** - Execute code (E2B only)
- **GET/POST /api/e2b/files** - File operations (E2B only)

### Storage (Persistent Data)
```
storage/
├── sessions/      # Session metadata
└── artifacts/     # Generated files
```

---

## Sandbox Providers

### E2B (Recommended)
**Cloud-based sandboxes**
- No infrastructure setup
- Auto-scaling
- Instant deployment
- Global CDN
- Built-in networking
- Requires API key
- Usage-based pricing

**Best for:** SaaS, serverless, production

### Docker (Optional)
**Self-hosted containers**
- Full control
- Free (infrastructure cost only)
- Offline execution
- Requires Docker daemon
- Manual scaling
- Infrastructure management

**Best for:** Development, on-premise, cost-sensitive

---

## Key Design Principles

### 1. Provider Abstraction
```python
# Same API, different providers
manager.start_sandbox(session_id, "Python3", provider="e2b")
manager.start_sandbox(session_id, "python:latest", provider="docker")
```

### 2. Stateless Execution
- Sessions are independent
- No shared state between sandboxes
- Clean lifecycle: create → execute → destroy

### 3. Separation of Concerns
- **Registry:** WHAT (config)
- **Orchestrator:** HOW (logic)
- **API:** WHO (interface)
- **Storage:** WHERE (data)

### 4. Security by Isolation
- Each session = isolated environment
- Resource limits enforced
- No cross-session contamination

---

## Integration Points

### For Agent Developers
```python
from orchestrator.lifecycle import Lifecycle

lifecycle = Lifecycle(
    storage_path="./storage",
    runtime_path="./sandbox_runtime",
    e2b_api_key="your_key"
)

# Start session
session = lifecycle.start(
    agent_config={"type": "code_executor"},
    environment="Python3",
    provider="e2b"
)

# Execute code
result = lifecycle.sandbox_mgr.execute_code(
    session_id=session["session_id"],
    code="print('Hello World')"
)

# Cleanup
lifecycle.stop(session["session_id"], session["sandbox_id"])
```

### Via REST API
```bash
# Create
curl -X POST http://localhost:8000/api/sessions \
  -d '{"environment": "Python3", "provider": "e2b"}'

# Execute
curl -X POST http://localhost:8000/api/e2b/execute \
  -d '{"session_id": "abc-123", "code": "print(42)"}'

# Destroy
curl -X DELETE http://localhost:8000/api/sessions/abc-123?sandbox_id=xyz
```

---

## See Also
- [E2B Setup Guide](e2b_guide.md) - Configuration and setup
- [E2B Examples](e2b_examples.md) - Code examples and patterns
