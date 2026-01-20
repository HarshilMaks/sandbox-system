# Sandbox System

A containerized sandbox environment for agent execution with declarative configuration.

## Structure

- `docker/` - Sandbox environment images
- `registry/` - Declarative configs (NO logic)
- `orchestrator/` - Brain of the system
- `api/` - Control surface
- `storage/` - Persistent storage (OUTSIDE sandbox)
- `sandbox_runtime/` - Mounted INSIDE sandbox
- `docs/` - Documentation
