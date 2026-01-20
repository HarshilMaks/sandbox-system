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
