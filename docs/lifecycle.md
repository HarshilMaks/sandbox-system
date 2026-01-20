# Lifecycle

## Session Creation
1. Client requests session via API
2. SessionManager creates session directory
3. SandboxManager starts container
4. StateManager initializes agent state
5. Return session_id and container_id

## Execution
1. Agent reads state from sandbox_runtime/agent/
2. Agent executes tasks using tools
3. Agent writes outputs to sandbox_runtime/workspace/
4. Agent updates state
5. Logs written to sandbox_runtime/logs/

## Session Destruction
1. Client requests session deletion
2. SandboxManager stops container
3. SessionManager moves data to storage/
4. Cleanup temporary files
5. Return success status

## State Flow
```
API → Orchestrator → Sandbox
    ↓
Storage ← Runtime
```
