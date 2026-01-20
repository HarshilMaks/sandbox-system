#!/usr/bin/env python3
"""Cleanup all E2B sandboxes."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
parent_dir = Path(__file__).parent.parent
load_dotenv(parent_dir / ".env")

def cleanup_all_sandboxes():
    """Kill all running E2B sandboxes."""
    api_key = os.getenv("E2B_API_KEY")
    if not api_key:
        print("❌ E2B_API_KEY not found in .env file")
        return
    
    try:
        from e2b_code_interpreter import Sandbox
        
        # List all running sandboxes
        print("🔍 Fetching running sandboxes from E2B API...")
        
        try:
            # Try to list sandboxes using the API
            import requests
            
            headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.e2b.dev/sandboxes",
                headers=headers
            )
            
            if response.status_code == 200:
                sandboxes = response.json()
                
                if not sandboxes:
                    print("✅ No running sandboxes found")
                    return
                
                print(f"Found {len(sandboxes)} running sandbox(es)\n")
                
                for sb in sandboxes:
                    sandbox_id = sb.get("sandboxID") or sb.get("sandbox_id") or sb.get("id")
                    if not sandbox_id:
                        continue
                    
                    try:
                        print(f"  Killing {sandbox_id}...")
                        sandbox = Sandbox(sandbox_id=sandbox_id, api_key=api_key)
                        sandbox.kill()
                        print(f"    ✓ Killed")
                    except Exception as e:
                        print(f"    ✗ Error: {e}")
                
                print(f"\n✅ Cleanup complete - killed {len(sandboxes)} sandbox(es)")
            else:
                print(f"❌ Failed to list sandboxes: {response.status_code}")
                print(f"Response: {response.text}")
                
        except ImportError:
            print("⚠️  'requests' module not found. Install with: pip install requests")
            print("Falling back to manual cleanup (enter sandbox IDs below)")
            
            while True:
                sandbox_id = input("\nEnter sandbox ID to kill (or press Enter to quit): ").strip()
                if not sandbox_id:
                    break
                
                try:
                    print(f"  Killing {sandbox_id}...")
                    sandbox = Sandbox(sandbox_id=sandbox_id, api_key=api_key)
                    sandbox.kill()
                    print(f"    ✓ Killed")
                except Exception as e:
                    print(f"    ✗ Error: {e}")
            
            print("\n✅ Cleanup complete")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_all_sandboxes()

