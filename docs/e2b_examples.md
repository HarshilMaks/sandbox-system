# Example: E2B Integration Usage

## Basic Usage

```python
from orchestrator.unified_manager import UnifiedSandboxManager

# Initialize manager
manager = UnifiedSandboxManager(e2b_api_key="your_key")

# Start E2B sandbox
result = manager.start_sandbox(
    session_id="test-123",
    environment="Python3",
    provider="e2b"
)
# Returns: {
#   "sandbox_id": "e2b_xyz",
#   "provider": "e2b",
#   "url": "https://..."
# }

# Execute code
execution = manager.execute_code(
    session_id="test-123",
    code="print('Hello E2B')",
    language="python"
)
# Returns: {
#   "stdout": "Hello E2B\n",
#   "stderr": "",
#   "results": []
# }

# Stop sandbox
manager.stop_sandbox("test-123", result["sandbox_id"])
```

## Comparison Example

```python
# Docker sandbox
docker_result = manager.start_sandbox(
    session_id="docker-123",
    environment="sandbox-python:latest",
    provider="docker"
)

# E2B sandbox
e2b_result = manager.start_sandbox(
    session_id="e2b-123",
    environment="Python3",
    provider="e2b"
)

# Both sessions managed through same interface
```

## API Usage

```bash
# Create E2B session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "code_executor",
    "environment": "Python3",
    "provider": "e2b"
  }'

# Execute code
curl -X POST http://localhost:8000/api/e2b/execute \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "code": "x = 2 + 2\nprint(x)",
    "language": "python"
  }'

# Response:
# {
#   "stdout": "4\n",
#   "stderr": "",
#   "error": null,
#   "results": []
# }
```

## Environment Variables

```bash
# .env file
E2B_API_KEY=your_api_key_here
SANDBOX_PROVIDER=e2b  # or "docker"
```

## Complete Flow

```python
from orchestrator.lifecycle import Lifecycle
from orchestrator.unified_manager import UnifiedSandboxManager

# Setup
lifecycle = Lifecycle(
    storage_path="./storage",
    runtime_path="./sandbox_runtime"
)

# Override sandbox manager with unified version
lifecycle.sandbox_mgr = UnifiedSandboxManager(e2b_api_key="your_key")

# Start with E2B
session = lifecycle.start(
    agent_config={"type": "code_executor"},
    environment="Python3",
    provider="e2b"
)

# Execute code
manager = lifecycle.sandbox_mgr
result = manager.execute_code(
    session_id=session["session_id"],
    code="import sys; print(sys.version)"
)

print(result["stdout"])  # Python version from E2B sandbox

# Cleanup
lifecycle.stop(session["session_id"], session["container_id"])
```
