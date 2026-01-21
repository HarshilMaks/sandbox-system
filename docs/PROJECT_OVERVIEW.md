# 🚀 Complete Project Overview: Sandbox System

## What Did We Build?

This is a **production-grade AI Agent System** that can:
1. **Chat with you** using Google Gemini AI
2. **Execute Python code** in secure cloud sandboxes (E2B)
3. **Remember conversations** across sessions
4. **Use custom Docker templates** with pre-installed packages

---

## 🎯 The Big Picture

```
┌──────────────────────────────────────────────────────────────────┐
│                         YOUR COMPUTER                            │
│                                                                  │
│  ┌────────────────┐                                              │
│  │   main.py      │  ← You run this to start the agent           │
│  │  (Entry Point) │                                              │
│  └───────┬────────┘                                              │
│          │                                                       │
│          ▼                                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      AGENT (agent.py)                      │  │
│  │   - Receives your message                                  │  │
│  │   - Decides if it needs to run code or just respond        │  │
│  │   - Maintains conversation history                         │  │
│  └─────┬─────────────────────────────┬────────────────────────┘  │
│        │                             │                           │
│        ▼                             ▼                           │
│  ┌──────────────┐            ┌──────────────────┐                │
│  │ Gemini API   │            │  Tool Executor   │                │
│  │ (gemini.py)  │            │  (executor.py)   │                │
│  │              │            │                  │                │
│  │ Thinks &     │            │ Routes to right  │                │
│  │ responds     │            │ tool             │                │
│  └──────────────┘            └────────┬─────────┘                │
│        ▲                              │                          │
│        │                              ▼                          │
│        │                     ┌──────────────────┐                │
│        │                     │  E2B Provider    │                │
│        │                     │   (e2b.py)       │                │
│        │                     └────────┬─────────┘                │
└────────│──────────────────────────────│──────────────────────────┘
         │                              │
         │ Internet                     │ Internet
         ▼                              ▼
┌──────────────┐              ┌─────────────────────────────────────┐
│  Google AI   │              │         E2B CLOUD                   │
│  (Gemini)    │              │  ┌─────────────────────────────┐    │
│              │              │  │     SANDBOX (Container)     │    │
│ "I'll help   │              │  │  ┌───────────────────────┐  │    │
│  you with    │              │  │  │  Python 3.12          │  │    │
│  that..."    │              │  │  │  + numpy              │  │    │
└──────────────┘              │  │  │  + pandas             │  │    │
                              │  │  │  + sklearn            │  │    │
                              │  │  │  + matplotlib         │  │    │
                              │  │  │  Your code runs here! │  │    │
                              │  │  └───────────────────────┘  │    │
                              │  └─────────────────────────────┘    │
                              └─────────────────────────────────────┘
```

---

## 📁 File-by-File Explanation

### **Entry Point**

| File | Purpose |
|------|---------|
| `main.py` | **Start here!** Runs the interactive chat agent. Connects everything together. |

### **Core Agent System** (`orchestrator/core/`)

| File | Purpose | Connects To |
|------|---------|-------------|
| `agent.py` | **The Brain** - Orchestrates everything. Takes your message, calls Gemini, decides if tools needed, returns response | gemini.py, executor.py, memory.py |
| `conversation.py` | Manages chat history (previous messages) | memory.py |
| `memory.py` | Stores session data persistently (JSON files) | storage/memory/ folder |

### **Providers** (`orchestrator/providers/`)

| File | Purpose | Connects To |
|------|---------|-------------|
| `gemini.py` | Talks to Google's Gemini AI API | Google Cloud (internet) |
| `e2b.py` | Creates & manages E2B sandboxes, runs code | E2B Cloud (internet) |

### **Tools** (`orchestrator/tools/`)

| File | Purpose | Connects To |
|------|---------|-------------|
| `base.py` | Base class for all tools (interface definition) | - |
| `registry.py` | Loads tool definitions from YAML files | registry/tools/*.yaml |
| `executor.py` | Routes tool calls to the right implementation | implementations.py, e2b.py |
| `implementations.py` | Actual tool code (execute_code, file_ops, etc.) | e2b.py |

### **Docker Template Files** (Root folder)

| File | Purpose |
|------|---------|
| `Dockerfile` | Defines custom sandbox image with numpy, pandas, etc. |
| `e2b.toml` | E2B configuration - template ID, start command |

### **Scripts** (`scripts/`)

| File | Purpose |
|------|---------|
| `custom_template.py` | **Test your custom template** - verifies packages work |
| `build_e2b_template.sh` | Builds and publishes Docker image to E2B |
| `verify.py` | Checks all imports work correctly |

---

## 🔄 How It All Flows

### **Flow 1: You Ask a Question (No Code)**

```
You: "What is machine learning?"
         │
         ▼
    ┌─────────┐
    │ main.py │ receives input
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Agent   │ sends to Gemini
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Gemini  │ "Machine learning is..."
    └────┬────┘
         │
         ▼
    Response printed to you
```

### **Flow 2: You Ask to Run Code**

```
You: "Calculate the mean of [1,2,3,4,5]"
         │
         ▼
    ┌─────────┐
    │ main.py │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Agent   │ → Gemini says "I need to use execute_code tool"
    └────┬────┘
         │
         ▼
    ┌──────────────┐
    │ Tool Executor│ → "execute_code" requested
    └────┬─────────┘
         │
         ▼
    ┌─────────────┐
    │ E2B Provider│ → sandbox.run_code("import numpy...")
    └────┬────────┘
         │
         ▼
    ┌─────────────────────┐
    │ E2B Cloud Sandbox   │ → Runs your Python code!
    │ (with numpy,pandas) │
    └────┬────────────────┘
         │
         ▼
    Result: "3.0" → back to Agent → back to you
```

---

## 🐳 Docker Template: Why & How

### **The Problem (Yesterday)**
- Default E2B sandbox has basic Python
- Every time you `import numpy`, E2B has to install it (slow!)
- Takes 10-30 seconds per package installation

### **The Solution (Today)**
- Build a **custom Docker template** with packages pre-installed
- E2B stores this template
- When you create a sandbox, packages are already there!
- **Result: Instant imports, 10-30x faster**

### **How the Template Works**

```
┌─────────────────────────────────────────────────────────────────┐
│  YOUR PROJECT                                                   │
│                                                                 │
│  Dockerfile ─────────────────────┐                              │
│  (defines what to install)       │                              │
│                                  │   e2b template build         │
│  e2b.toml ───────────────────────┼──────────────────────────►   │
│  (configuration)                 │                              │
│                                  │                              │
└──────────────────────────────────┘                              │
                                                                  │
                                                                  ▼
                                              ┌───────────────────────────┐
                                              │      E2B CLOUD            │
                                              │                           │
                                              │  Template stored:         │
                                              │  en7sb4k1n268scs49jnj     │
                                              │                           │
                                              │  ┌─────────────────────┐  │
                                              │  │ Pre-installed:      │  │
                                              │  │ • numpy 1.26.4      │  │
                                              │  │ • pandas 2.2.3      │  │
                                              │  │ • sklearn 1.6.1     │  │
                                              │  │ • matplotlib 3.10.3 │  │
                                              │  └─────────────────────┘  │
                                              └───────────────────────────┘
```

---

## 🏃 How To Run Everything

### **Option 1: Run the Full Agent (Chat + Code Execution)**

```bash
cd /home/harshil/sandbox-system
python main.py
```

**What happens:**
1. Agent starts
2. Creates E2B sandbox
3. You can chat with it
4. Ask it to run code → it executes in the sandbox

### **Option 2: Test Custom Template Only**

```bash
cd /home/harshil/sandbox-system
python scripts/custom_template.py
```

**What happens:**
1. Creates a sandbox using your custom template
2. Verifies numpy, pandas, sklearn, matplotlib work
3. Shows you the versions installed

### **Option 3: Rebuild Custom Template**

```bash
cd /home/harshil/sandbox-system
e2b template build -c "/root/.jupyter/start-up.sh"
```

**What happens:**
1. Builds Docker image from `Dockerfile`
2. Uploads to E2B cloud
3. Gives you a new template ID

---

## 🔗 The Connection: Agent + Custom Template

To use your custom template in the agent, update `e2b.py`:

```python
# In orchestrator/providers/e2b.py

def create_sandbox(self, session_id: str, template: Optional[str] = None) -> str:
    # Use your custom template!
    template = template or "en7sb4k1n268scs49jnj"  # Add this default
    
    sandbox = Sandbox(
        template=template,
        api_key=self.api_key
    )
```

Or call it explicitly:

```python
e2b_provider.create_sandbox(session_id, template="en7sb4k1n268scs49jnj")
```

---

## 📊 Summary: What We Built

| Day | What We Did | Result |
|-----|-------------|--------|
| **Yesterday** | Built the Agent framework | Chat with Gemini, execute code in E2B |
| **Today** | Built custom Docker template | Pre-installed packages, faster execution |

### **Final Architecture**

```
sandbox-system/
├── main.py                 # 🚀 Entry point - run this!
│
├── orchestrator/
│   ├── core/
│   │   ├── agent.py        # 🧠 The brain - orchestrates everything
│   │   ├── conversation.py # 💬 Chat history manager
│   │   └── memory.py       # 💾 Persistent storage
│   │
│   ├── providers/
│   │   ├── gemini.py       # 🤖 Talks to Google Gemini
│   │   └── e2b.py          # 📦 Creates & manages sandboxes
│   │
│   └── tools/
│       ├── executor.py     # 🔧 Routes tool calls
│       └── implementations.py # ⚙️ Tool implementations
│
├── Dockerfile              # 🐳 Custom sandbox definition
├── e2b.toml               # ⚙️ E2B template config
│
└── scripts/
    └── custom_template.py  # 🧪 Test your custom template
```

---

## ❓ Common Questions

**Q: Do I need Docker installed locally?**
A: No! E2B builds the Docker image in their cloud. You just need the `e2b` CLI.

**Q: What's the difference between default and custom template?**
A: Default = basic Python. Custom = Python + your packages (numpy, pandas, etc.)

**Q: How do I add more packages?**
A: Edit `Dockerfile`, add packages, run `e2b template build -c "/root/.jupyter/start-up.sh"`

**Q: Why the weird start command?**
A: It starts the Jupyter kernel server on port 49999, which `run_code()` needs.

---

## 🎉 You Now Have

1. ✅ An AI agent that can chat and run code
2. ✅ Secure cloud sandboxes for code execution
3. ✅ Custom Docker template with data science packages
4. ✅ Understanding of how everything connects!
