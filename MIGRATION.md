# OpenAI to Gemini Migration Guide

## Changes Made

This document outlines the complete migration from OpenAI API to Google Gemini API.

## Summary of Changes

### 1. Dependencies Updated
**File**: `requirements.txt`

**Before**:
```txt
openai>=1.54.0
```

**After**:
```txt
google-generativeai>=0.3.0
```

### 2. Provider Implementation
**Created**: `orchestrator/providers/gemini.py`

New provider implementing the same interface as OpenAI provider:
- `chat_completion()` - Non-streaming completion
- `stream_completion()` - Streaming completion  
- `_convert_messages()` - OpenAI→Gemini message format conversion
- `_convert_tools()` - OpenAI→Gemini tool format conversion

**Removed**: `orchestrator/providers/openai.py`

### 3. Agent Configuration
**File**: `orchestrator/core/agent.py`

**Before**:
```python
from orchestrator.providers.openai import OpenAIProvider
model: str = "gpt-4o-mini"
```

**After**:
```python
from orchestrator.providers.gemini import GeminiProvider
model: str = "gemini-2.0-flash-exp"
```

### 4. Example Code
**File**: `examples/conversational_agent.py`

**Before**:
```python
from orchestrator.providers.openai import OpenAIProvider

openai_provider = OpenAIProvider(
    api_key=os.getenv("OPENAI_API_KEY")
)

config = AgentConfig(
    model="gpt-4o-mini",
    # ...
)

agent = Agent(
    config=config,
    llm_provider=openai_provider,
    # ...
)
```

**After**:
```python
from orchestrator.providers.gemini import GeminiProvider

gemini_provider = GeminiProvider(
    api_key=os.getenv("GEMINI_API_KEY")
)

config = AgentConfig(
    model="gemini-2.0-flash-exp",
    # ...
)

agent = Agent(
    config=config,
    llm_provider=gemini_provider,
    # ...
)
```

### 5. Environment Variables
**File**: `.env.example`

**Before**:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**After**:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 6. Documentation
**File**: `README.md`

Updated all references:
- Feature list: "OpenAI" → "Google Gemini"
- Project structure: `openai.py` → `gemini.py`
- Environment setup: `OPENAI_API_KEY` → `GEMINI_API_KEY`
- Example code: `OpenAIProvider` → `GeminiProvider`
- Model references: `gpt-4o-mini` → `gemini-2.0-flash-exp`

## API Compatibility

### Message Format Conversion

**OpenAI Format**:
```python
{
    "role": "user",
    "content": "Hello"
}
```

**Gemini Format**:
```python
{
    "role": "user",
    "parts": [{"text": "Hello"}]
}
```

The `GeminiProvider._convert_messages()` method handles this conversion automatically.

### Tool Format Conversion

**OpenAI Format**:
```python
{
    "type": "function",
    "function": {
        "name": "execute_code",
        "description": "Execute Python code",
        "parameters": {
            "type": "object",
            "properties": {...}
        }
    }
}
```

**Gemini Format**:
```python
{
    "function_declarations": [{
        "name": "execute_code",
        "description": "Execute Python code",
        "parameters": {
            "type": "object",
            "properties": {...}
        }
    }]
}
```

The `GeminiProvider._convert_tools()` method handles this conversion automatically.

## Files Removed

### Legacy Orchestration Files
1. `orchestrator/lifecycle.py` - Old lifecycle management
2. `orchestrator/unified_manager.py` - Old Docker/E2B manager
3. `orchestrator/session_manager.py` - Old session management
4. `orchestrator/state_manager.py` - Old state management
5. `orchestrator/e2b_manager.py` - Old E2B manager (replaced by providers/e2b.py)

### Old Provider
6. `orchestrator/providers/openai.py` - Old OpenAI integration

### API Routes
7. `api/` directory - FastAPI routes that referenced deleted modules

## Getting Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add to `.env`: `GEMINI_API_KEY=your_key_here`

**Note**: Gemini API is **free** for moderate usage, unlike OpenAI which is paid from the start.

## Model Comparison

| OpenAI Model | Gemini Equivalent | Use Case |
|--------------|-------------------|----------|
| gpt-4o-mini  | gemini-2.0-flash-exp | Fast, cost-effective responses |
| gpt-4o       | gemini-1.5-pro | Complex reasoning, longer context |
| gpt-4-turbo  | gemini-1.5-pro | Advanced capabilities |

## Verification Steps

1. **Install new dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Update environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Verify imports compile**:
   ```bash
   python -m py_compile examples/conversational_agent.py
   ```

4. **Test Gemini provider**:
   ```python
   from orchestrator.providers.gemini import GeminiProvider
   
   provider = GeminiProvider()
   response = provider.chat_completion(
       messages=[{"role": "user", "content": "Hello"}],
       model="gemini-2.0-flash-exp"
   )
   print(response)
   ```

5. **Run full example**:
   ```bash
   python examples/conversational_agent.py
   ```

## Breaking Changes

### For External Code

If you have code importing the old provider:

**Old**:
```python
from orchestrator.providers.openai import OpenAIProvider
provider = OpenAIProvider(api_key="...")
```

**New**:
```python
from orchestrator.providers.gemini import GeminiProvider
provider = GeminiProvider(api_key="...")
```

### Model Names

Update all model references:
- `gpt-4o-mini` → `gemini-2.0-flash-exp`
- `gpt-4o` → `gemini-1.5-pro`
- `gpt-4-turbo` → `gemini-1.5-pro`

### Environment Variables

Update your `.env` file:
- `OPENAI_API_KEY` → `GEMINI_API_KEY`

## Rollback (If Needed)

If you need to rollback to OpenAI:

1. Restore `requirements.txt`:
   ```txt
   openai>=1.54.0
   ```

2. Recreate `orchestrator/providers/openai.py` from git history

3. Update imports in:
   - `orchestrator/core/agent.py`
   - `examples/conversational_agent.py`

4. Update `.env`: `OPENAI_API_KEY=...`

## Cost Comparison

| Provider | Model | Cost (Input) | Cost (Output) | Free Tier |
|----------|-------|--------------|---------------|-----------|
| OpenAI | gpt-4o-mini | $0.150/1M tokens | $0.600/1M tokens | None |
| Gemini | gemini-2.0-flash | **FREE** | **FREE** | 1M tokens/min |
| OpenAI | gpt-4o | $2.50/1M tokens | $10.00/1M tokens | None |
| Gemini | gemini-1.5-pro | **FREE** | **FREE** | 50 tokens/min |

**Reason for migration**: Gemini provides free tier with generous limits, making it cost-effective for development and moderate production use.

## Additional Features in Gemini

Gemini provider supports:
- ✅ Streaming responses
- ✅ Function calling (tools)
- ✅ Long context (up to 2M tokens in gemini-1.5-pro)
- ✅ Multi-modal (text, images, audio - not yet implemented)
- ✅ Temperature control
- ✅ Token limits
- ✅ Async operations

## Support

For issues with:
- **Gemini API**: [Google AI Studio Docs](https://ai.google.dev/docs)
- **E2B Sandboxes**: [E2B Documentation](https://e2b.dev/docs)
- **This system**: Check `ARCHITECTURE.md` for file structure and connections
