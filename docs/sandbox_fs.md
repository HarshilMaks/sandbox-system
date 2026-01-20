# Sandbox Filesystem

## Structure
```
/sandbox/
├── agent/           # Agent state and memory
├── workspace/       # Working directory for agent
├── tools/           # Executable tools
├── logs/            # All logs
└── meta/            # Session metadata
```

## Mounts
- Host: `./sandbox_runtime/` → Container: `/sandbox/`
- Read/Write access
- Persisted to `storage/` on session end

## Isolation
- Network: Optional (configured per environment)
- Filesystem: Restricted to /sandbox/
- Resources: CPU and memory limits

## Security
- No root access in container
- Tool execution sandboxed
- Timeout enforcement
- Resource quotas
