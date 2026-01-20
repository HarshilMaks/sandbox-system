# E2B Configuration

## Setup

1. **Get API Key**
   ```bash
   # Sign up at https://e2b.dev
   # Get your API key from dashboard
   ```

2. **Set Environment Variable**
   ```bash
   export E2B_API_KEY="your_api_key_here"
   ```

   Or add to `.env`:
   ```
   E2B_API_KEY=your_api_key_here
   ```

3. **Install Dependencies**
   ```bash
   # Using uv (recommended)
   uv pip install -e .
   
   # Or install just E2B SDK
   uv pip install e2b-code-interpreter
   ```

## Usage

### Create E2B Session
```bash
POST /api/sessions
{
  "agent": "code_executor",
  "environment": "e2b-python",
  "provider": "e2b"
}
```

### Execute Code
```bash
POST /api/e2b/execute
{
  "session_id": "abc-123",
  "code": "print('Hello from E2B')",
  "language": "python"
}
```

### File Operations
```bash
# List files
GET /api/e2b/files/abc-123?directory=/workspace

# Read file
GET /api/e2b/files/abc-123/output.txt

# Write file
POST /api/e2b/files
{
  "session_id": "abc-123",
  "file_path": "/workspace/data.csv",
  "content": "base64_encoded_content"
}
```

## E2B vs Docker

| Feature | Docker | E2B |
|---------|--------|-----|
| **Deployment** | Self-hosted | Cloud-hosted |
| **Setup** | Docker daemon required | API key only |
| **Scaling** | Manual | Automatic |
| **Networking** | Local | Global CDN |
| **Pricing** | Free (infrastructure cost) | Usage-based |
| **File Persistence** | Volume mounts | API-based |
| **Latency** | Low (local) | Network-dependent |

## When to Use E2B

**Use E2B when:**
- You don't want to manage Docker infrastructure
- Need auto-scaling for multiple concurrent sessions
- Want zero-setup deployment
- Building a SaaS product

**Use Docker when:**
- Need complete control over infrastructure
- Have specific networking requirements
- Want offline execution
- Cost-sensitive for high volume

## E2B Templates

Available templates:
- `Python3` - Python 3.11 with common packages
- `Node` - Node.js environment
- `Bash` - Linux shell environment

Custom templates can be created via E2B dashboard.
