# Stateful Sandbox System for Running AI Agents

A containerized sandbox system that provides isolated execution environments for AI agents with persistent state management.

## What This System Does

- **Creates isolated execution environments (sandbox)** - Containerized workspaces with controlled resources
- **Maintains session state** - Persistent agent state, memory, and progress tracking
- **Allows code/tool execution** - Secure execution of code and tools within sandbox boundaries
- **Stores logs & artifacts** - Complete audit trail and output preservation
- **Destroys everything cleanly** - Full lifecycle management with proper cleanup

## What This System Does NOT Do

- Agent intelligence or reasoning
- Multi-agent orchestration or debates
- Agent prompt engineering or optimization

> **This is a sandbox execution platform, not an agent framework.**

## Structure

- `docker/` - Sandbox environment images
- `registry/` - Declarative configs (NO logic)
- `orchestrator/` - Session and sandbox lifecycle management
- `api/` - Control surface for external systems
- `storage/` - Persistent storage (OUTSIDE sandbox)
- `sandbox_runtime/` - Execution environment (INSIDE sandbox)
- `docs/` - Documentation
