#!/usr/bin/env python3
"""List available Gemini models."""
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load .env from parent directory
parent_dir = Path(__file__).parent.parent
load_dotenv(parent_dir / ".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Gemini models:")
print("=" * 60)

try:
    # List all models
    for model in client.models.list():
        if "gemini" in model.name.lower():
            print(f"✓ {model.name}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

