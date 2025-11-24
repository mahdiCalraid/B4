from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ExecutionContext:
    """Shared context for workflow execution."""
    def __init__(self, execution_id: str, env: Dict[str, str] = None):
        self.execution_id = execution_id
        self.env = env or {}
        self.node_outputs: Dict[str, Any] = {}
        self.state: str = "running"
        self.error: Optional[str] = None
        self.steps: list = []

    def set_output(self, node_id: str, output: Any):
        self.node_outputs[node_id] = output
        
    def get_output(self, node_id: str) -> Optional[Any]:
        return self.node_outputs.get(node_id)

class BaseNodeRunner(ABC):
    """Base class for all node runners."""
    
    @abstractmethod
    async def run(self, config: Dict[str, Any], inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute the node logic.
        
        Args:
            config: The static configuration from the node instance (e.g. table name).
            inputs: The resolved input data from upstream nodes.
            context: The global execution context.
            
        Returns:
            The output dictionary of the node.
        """
        pass
