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
- Environments (Docker + E2B)
- Agents
- Tools
- Prompts

### Orchestrator
The brain of the system:
- Session management
- Sandbox lifecycle (Docker + E2B)
- State persistence
- High-level flow control
- Unified sandbox management

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
Mounted INSIDE sandbox (Docker) or accessed via API (E2B):
- Agent state
- Workspace
- Tools
- Logs

### Sandbox Providers

#### Docker (Local)
- Self-hosted containers
- Volume mounts for file access
- Direct container control
- Best for: Development, on-premise, high volume

#### E2B (Cloud)
- Managed cloud sandboxes
- API-based file operations
- Auto-scaling
- Best for: SaaS, serverless, rapid deployment
