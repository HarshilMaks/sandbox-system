"""Agent state persistence."""
import json
from pathlib import Path


class StateManager:
    """Manages agent state read/write operations.
    
    Stores state, memory, and progress for external agent systems.
    This is a state store only - not an agent runtime.
    """
    
    def __init__(self, runtime_path: str):
        self.runtime_path = Path(runtime_path)
    
    def read_state(self, session_id: str) -> dict:
        """Read agent state."""
        state_file = self.runtime_path / "agent" / "state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def write_state(self, session_id: str, state: dict) -> bool:
        """Write agent state."""
        state_file = self.runtime_path / "agent" / "state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        return True
