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
   pip install e2b-code-interpreter
   ```

## Quick Usage

### Default Template
```python
from e2b_code_interpreter import Sandbox

sandbox = Sandbox(api_key=api_key)
result = sandbox.run_code("print('Hello from E2B!')")
print(result.logs.stdout)
sandbox.kill()
```

### Custom Template (with pre-installed packages)
```python
from e2b_code_interpreter import Sandbox

# Use our custom template with numpy, pandas, sklearn, etc.
sandbox = Sandbox(
    template="en7sb4k1n268scs49jnj",
    api_key=api_key
)

result = sandbox.run_code("""
import numpy as np
import pandas as pd
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
""")
print(result.logs.stdout)
sandbox.kill()
```

## Custom Template

### Pre-installed Packages
Template ID: `en7sb4k1n268scs49jnj`
- numpy (1.26.4)
- pandas (2.2.3)
- scikit-learn (1.6.1)
- matplotlib (3.10.3)
- requests
- beautifulsoup4

### Build Your Own Template

1. **Edit Dockerfile** - Add your packages:
   ```dockerfile
   FROM e2bdev/code-interpreter:latest
   RUN pip install --no-cache-dir your-packages
   ```

2. **Build with start command** (CRITICAL!):
   ```bash
   e2b template build -c "/root/.jupyter/start-up.sh"
   ```

3. **Use the template**:
   ```python
   sandbox = Sandbox(template="your-new-template-id")
   ```

## API Endpoints

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
```

## E2B Templates

| Template | Description |
|----------|-------------|
| Default | Python 3.12, basic packages |
| `en7sb4k1n268scs49jnj` | Python 3.12 + numpy, pandas, sklearn, matplotlib |

Custom templates can be created via E2B dashboard.
