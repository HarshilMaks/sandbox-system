#!/usr/bin/env python3
"""
Example: Using Custom E2B Template
This demonstrates how to use your custom Docker image with E2B sandboxes.
"""

import os
from pathlib import Path
from e2b_code_interpreter import Sandbox

# Load .env file
def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def main():
    """Demo custom template usage."""
    
    # Load .env file first
    load_env()
    
    # Get API key
    api_key = os.getenv("E2B_API_KEY")
    if not api_key:
        print("❌ E2B_API_KEY not set!")
        print("Set it with: export E2B_API_KEY='your_key'")
        print("Or add it to .env file")
        return
    
    print("🚀 E2B Custom Template Demo")
    print("=" * 50)
    
    # Method 1: Using default template
    print("\n📦 Method 1: Default Template")
    print("-" * 50)
    sandbox_default = Sandbox(api_key=api_key)
    print(f"✓ Sandbox created: {sandbox_default.sandbox_id}")
    
    result = sandbox_default.run_code("import sys; print(f'Python: {sys.version}')")
    print(f"Output: {result.logs.stdout}")
    sandbox_default.kill()
    print("✓ Sandbox closed")
    
    # Method 2: Using custom template (replace with your template ID)
    print("\n🎨 Method 2: Custom Template")
    print("-" * 50)
    
    # Replace this with your actual template ID after running e2b template build
    CUSTOM_TEMPLATE_ID = "en7sb4k1n268scs49jnj"  # Your custom template ID
    
    print(f"Template ID: {CUSTOM_TEMPLATE_ID}")
    
    if CUSTOM_TEMPLATE_ID == "your-custom-template-id":
        print("⚠️  Please update CUSTOM_TEMPLATE_ID with your actual template ID")
        print("   Run: ./scripts/build_e2b_template.sh to create your template")
    else:
        # Increase timeout significantly for initial setup
        sandbox_custom = Sandbox(
            template=CUSTOM_TEMPLATE_ID,
            api_key=api_key,
            timeout=180  # 3 minutes for first run
        )
        print(f"✓ Custom sandbox created: {sandbox_custom.sandbox_id}")
        print("⏳ Waiting for code interpreter to start (this may take a moment)...")
        
        # Test custom packages
        test_code = """
print("Testing custom template...")
import sys
print(f"Python version: {sys.version}")

try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
except ImportError as e:
    print(f"NumPy error: {e}")

try:
    import pandas as pd
    print(f"Pandas: {pd.__version__}")
except ImportError as e:
    print(f"Pandas error: {e}")

try:
    import sklearn
    print(f"Scikit-learn: {sklearn.__version__}")
except ImportError as e:
    print(f"Scikit-learn error: {e}")

try:
    import matplotlib
    print(f"Matplotlib: {matplotlib.__version__}")
except ImportError as e:
    print(f"Matplotlib error: {e}")

print("All packages working!")
"""
        
        result = sandbox_custom.run_code(test_code)
        print(f"Output:\n{result.logs.stdout}")
        
        if result.error:
            print(f"Error: {result.error}")
        
        sandbox_custom.kill()
        print("✓ Custom sandbox closed")
    
    print("\n" + "=" * 50)
    print("✓ Demo complete!")

if __name__ == "__main__":
    main()
