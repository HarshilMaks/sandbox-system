"""Sandbox lifecycle management."""
import docker


class SandboxManager:
    """Manages isolated container lifecycle for code execution.
    
    Provides secure, resource-controlled execution environments.
    Agent code runs INSIDE these containers.
    """
    
    def __init__(self):
        self.client = docker.from_env()
    
    def start_sandbox(self, session_id: str, environment: str) -> str:
        """Start a sandbox container."""
        container = self.client.containers.run(
            environment,
            detach=True,
            name=f"sandbox_{session_id}",
            volumes={
                f"./sandbox_runtime": {"bind": "/sandbox", "mode": "rw"}
            }
        )
        return container.id
    
    def stop_sandbox(self, container_id: str) -> bool:
        """Stop a sandbox container."""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove()
            return True
        except Exception as e:
            print(f"Error stopping sandbox: {e}")
            return False
