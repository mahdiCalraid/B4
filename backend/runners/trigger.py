from typing import Dict, Any
from .base import BaseNodeRunner, ExecutionContext

class TriggerRunner(BaseNodeRunner):
    async def run(self, config: Dict[str, Any], inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        # Triggers are usually entry points, so they might just pass data through
        # or simply signal start.
        return {
            "status": "triggered", 
            "timestamp": "now",
            **inputs # Pass through inputs (like 'text' from frontend)
        }
