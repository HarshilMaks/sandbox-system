#!/usr/bin/env python3
"""
Generate a visual connection map of all imports in the system.
"""
import ast
import sys
from pathlib import Path
from typing import Dict, Set, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_imports(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return set()

def filter_local_imports(imports: Set[str]) -> Set[str]:
    """Filter to only local orchestrator imports."""
    return {imp for imp in imports if imp.startswith('orchestrator')}

def main():
    """Generate connection map."""
    project_root = Path(__file__).parent
    
    # Find all Python files
    py_files = list(project_root.rglob("*.py"))
    py_files = [f for f in py_files if not f.name.startswith("__")]
    py_files = [f for f in py_files if ".venv" not in str(f)]
    py_files = [f for f in py_files if "verify" not in str(f)]
    py_files = [f for f in py_files if "map_connections" not in str(f)]
    
    # Build connection map
    connections: Dict[str, Set[str]] = {}
    
    for file_path in py_files:
        relative_path = file_path.relative_to(project_root)
        module_name = str(relative_path).replace("/", ".").replace(".py", "")
        
        imports = get_imports(file_path)
        local_imports = filter_local_imports(imports)
        
        if module_name or local_imports:
            connections[module_name] = local_imports
    
    # Print connection map
    print("=" * 80)
    print("SANDBOX SYSTEM - FILE CONNECTION MAP")
    print("=" * 80)
    print()
    
    # Sort by dependency level (files with fewer imports first)
    sorted_files = sorted(connections.items(), key=lambda x: len(x[1]))
    
    print("📊 DEPENDENCY LEVELS")
    print("─" * 80)
    print()
    
    # Level 0: No dependencies
    print("🟢 LEVEL 0 - Independent Modules (No Internal Dependencies)")
    print("─" * 80)
    level0 = [(name, deps) for name, deps in sorted_files if len(deps) == 0]
    for name, deps in level0:
        print(f"  • {name}")
    print()
    
    # Level 1: 1-2 dependencies
    print("🟡 LEVEL 1 - Basic Dependencies (1-2 imports)")
    print("─" * 80)
    level1 = [(name, deps) for name, deps in sorted_files if 1 <= len(deps) <= 2]
    for name, deps in level1:
        print(f"  • {name}")
        for dep in sorted(deps):
            print(f"      → {dep}")
    print()
    
    # Level 2: 3-4 dependencies
    print("🟠 LEVEL 2 - Moderate Dependencies (3-4 imports)")
    print("─" * 80)
    level2 = [(name, deps) for name, deps in sorted_files if 3 <= len(deps) <= 4]
    for name, deps in level2:
        print(f"  • {name}")
        for dep in sorted(deps):
            print(f"      → {dep}")
    print()
    
    # Level 3+: Many dependencies
    print("🔴 LEVEL 3+ - Complex Dependencies (5+ imports)")
    print("─" * 80)
    level3 = [(name, deps) for name, deps in sorted_files if len(deps) >= 5]
    for name, deps in level3:
        print(f"  • {name} ({len(deps)} dependencies)")
        for dep in sorted(deps):
            print(f"      → {dep}")
    print()
    
    print("=" * 80)
    print("📈 STATISTICS")
    print("─" * 80)
    print(f"Total files: {len(connections)}")
    print(f"Level 0 (independent): {len(level0)}")
    print(f"Level 1 (basic): {len(level1)}")
    print(f"Level 2 (moderate): {len(level2)}")
    print(f"Level 3+ (complex): {len(level3)}")
    print()
    
    # Calculate which files are most depended upon
    print("=" * 80)
    print("🎯 MOST IMPORTED MODULES")
    print("─" * 80)
    import_counts: Dict[str, int] = {}
    for name, deps in connections.items():
        for dep in deps:
            import_counts[dep] = import_counts.get(dep, 0) + 1
    
    sorted_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)
    for module, count in sorted_imports[:10]:
        print(f"  {count}× {module}")
    print()
    
    print("=" * 80)
    print()
    print("✅ Connection map generated successfully!")
    print()
    print("Key findings:")
    print(f"  • {len(level0)} independent modules (good for testing)")
    print(f"  • {len(level3)} complex modules (main entry points)")
    print(f"  • Most depended on: {sorted_imports[0][0] if sorted_imports else 'None'}")
    print()

if __name__ == "__main__":
    main()
