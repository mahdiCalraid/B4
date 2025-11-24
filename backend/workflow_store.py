import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkflowStore:
    """Manages filesystem storage for workflows."""
    
    def __init__(self):
        self._base_path = Path(__file__).parent / "workflows"
        self._base_path.mkdir(exist_ok=True)
        
    def list_workflows(self) -> List[Dict]:
        """List all saved workflows (metadata only)."""
        workflows = []
        for file_path in self._base_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    workflows.append({
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "description": data.get("description", ""),
                        "updated_at": data.get("updated_at", "")
                    })
            except Exception as e:
                logger.error(f"Failed to load workflow {file_path}: {e}")
        return workflows

    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get a full workflow by ID."""
        file_path = self._base_path / f"{workflow_id}.json"
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read workflow {workflow_id}: {e}")
            return None

    def save_workflow(self, workflow: Dict) -> str:
        """Save a workflow."""
        if not workflow.get("id"):
            workflow["id"] = str(uuid.uuid4())
            
        workflow["updated_at"] = datetime.now().isoformat()
        
        file_path = self._base_path / f"{workflow['id']}.json"
        
        with open(file_path, 'w') as f:
            json.dump(workflow, f, indent=2)
            
        return workflow["id"]

# Global store instance
workflow_store = WorkflowStore()
