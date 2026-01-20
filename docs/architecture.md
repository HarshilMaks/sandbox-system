# Architecture

## Overview
The sandbox system provides isolated execution environments for AI agents with declarative configuration.

## Components

### Registry
Declarative YAML configs with NO logic:
- Environments
- Agents
- Tools
- Prompts

### Orchestrator
The brain of the system:
- Session management
- Sandbox lifecycle
- State persistence
- High-level flow control

### API
Control surface for external interaction:
- REST endpoints
- Session management
- Sandbox control

### Storage
Persistent storage OUTSIDE sandbox:
- Session data
- Artifacts
- Logs

### Sandbox Runtime
Mounted INSIDE sandbox:
- Agent state
- Workspace
- Tools
- Logs
