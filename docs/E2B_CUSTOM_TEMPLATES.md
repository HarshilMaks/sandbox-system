# E2B Custom Docker Templates - Complete Guide

## ✅ Custom Docker Images Work!

Custom Docker images work with E2B Code Interpreter when you include the correct start command.

---

## Quick Start

### 1. Create Dockerfile
```dockerfile
FROM e2bdev/code-interpreter:latest

RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    scikit-learn \
    requests \
    beautifulsoup4
```

### 2. Build with Start Command (CRITICAL!)
```bash
e2b template build -c "/root/.jupyter/start-up.sh"
```

### 3. Use in Python
```python
from e2b_code_interpreter import Sandbox

sandbox = Sandbox(template="en7sb4k1n268scs49jnj", api_key=api_key)
result = sandbox.run_code("import numpy; print(numpy.__version__)")
# Output: 1.26.4 ✅
sandbox.kill()
```

---

## The Critical Fix

**Without start command (FAILS):**
```bash
e2b template build  # ❌ Port 49999 not open error
```

**With start command (WORKS):**
```bash
e2b template build -c "/root/.jupyter/start-up.sh"  # ✅
```

The `-c` flag tells E2B to run the Jupyter kernel startup script when sandbox boots.

---

## Working Configuration

### Dockerfile
```dockerfile
# E2B Custom Sandbox Dockerfile for Code Interpreter
FROM e2bdev/code-interpreter:latest

# Install custom Python packages
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    scikit-learn \
    requests \
    beautifulsoup4
```

### e2b.toml
```toml
team_id = "your-team-id"
dockerfile = "Dockerfile"
template_id = "en7sb4k1n268scs49jnj"
start_cmd = "/root/.jupyter/start-up.sh"
```

---

## Verified Working

**Template ID:** `en7sb4k1n268scs49jnj`

| Package | Version |
|---------|---------|
| Python | 3.12.12 |
| NumPy | 1.26.4 |
| Pandas | 2.2.3 |
| Scikit-learn | 1.6.1 |
| Matplotlib | 3.10.3 |

---

## Commands Reference

```bash
# Login
e2b auth login

# Build (MUST include -c flag!)
e2b template build -c "/root/.jupyter/start-up.sh"

# List templates
e2b template list

# Delete template
e2b template delete <template-id>
```

---

## Files in This Project

| File | Purpose |
|------|---------|
| `Dockerfile` | Custom image definition |
| `e2b.toml` | E2B template configuration |
| `scripts/custom_template.py` | Test the custom template |
| `scripts/build_e2b_template.sh` | Build helper script |

---

## Test Your Template

```bash
python scripts/custom_template.py
```

Expected output:
```
🚀 E2B Custom Template Demo
✓ Custom sandbox created
NumPy: 1.26.4
Pandas: 2.2.3
Scikit-learn: 1.6.1
Matplotlib: 3.10.3
All packages working!
```
