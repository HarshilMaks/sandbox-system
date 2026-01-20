#!/usr/bin/env python3
"""
Verify all imports and connections in the sandbox system.
Checks that all files can be imported without errors.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_import(module_path: str, description: str) -> bool:
    """Try to import a module and report result."""
    try:
        __import__(module_path)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def main():
    """Run all import checks."""
    print("=" * 60)
    print("Sandbox System - Import Verification")
    print("=" * 60)
    print()
    
    checks = [
        # Core modules
        ("orchestrator.core.memory", "Core: Memory Store"),
        ("orchestrator.core.conversation", "Core: Conversation Manager"),
        ("orchestrator.core.agent", "Core: Agent"),
        
        # Providers
        ("orchestrator.providers.gemini", "Provider: Gemini (Google)"),
        ("orchestrator.providers.e2b", "Provider: E2B Sandbox"),
        
        # Tools
        ("orchestrator.tools.base", "Tools: Base Classes"),
        ("orchestrator.tools.registry", "Tools: Registry"),
        ("orchestrator.tools.implementations", "Tools: Implementations"),
        ("orchestrator.tools.executor", "Tools: Executor"),
        
        # Utils
        ("orchestrator.utils.logging", "Utils: Logging"),
        ("orchestrator.utils.retry", "Utils: Retry Logic"),
        ("orchestrator.utils.streaming", "Utils: Streaming"),
        
        # Examples
        ("main", "Main: Agent Runner"),
    ]
    
    results = []
    for module_path, description in checks:
        result = check_import(module_path, description)
        results.append(result)
    
    print()
    print("=" * 60)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"✅ All {total_count} imports successful!")
        print("=" * 60)
        print()
        print("System is ready to use. Next steps:")
        print("1. Add API keys to .env file:")
        print("   - GEMINI_API_KEY (get from https://aistudio.google.com/app/apikey)")
        print("   - E2B_API_KEY (get from https://e2b.dev)")
        print()
        print("2. Run the example:")
        print("   python main.py")
        return 0
    else:
        print(f"❌ {success_count}/{total_count} imports successful")
        print(f"⚠️  {total_count - success_count} imports failed")
        print("=" * 60)
        print()
        print("Please check the errors above and ensure:")
        print("1. All dependencies are installed: uv pip install -r requirements.txt")
        print("2. Python version is 3.10 or higher")
        return 1

if __name__ == "__main__":
    sys.exit(main())
