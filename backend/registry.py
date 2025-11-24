import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib
import sys

# Add backend to path to ensure modules can be imported
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class NodeRegistry:
    """
    Static registry that loads nodes from node_registry.json.
    """
    
    def __init__(self):
        self.nodes: List[Dict[str, Any]] = []
        self._base_path = Path(__file__).parent
        self._registry_file = self._base_path / "node_registry.json"
        self._schema_file = self._base_path / "schema" / "node_schema.json"
        self.scan_all()
        
    def scan_all(self):
        """Load nodes from the static registry file."""
        self.nodes = []
        
        if not self._registry_file.exists():
            logger.error(f"Registry file not found: {self._registry_file}")
            return

        try:
            with open(self._registry_file, 'r') as f:
                data = json.load(f)
                raw_nodes = data.get("nodes", [])
                
            for node_entry in raw_nodes:
                try:
                    loaded_node = self._load_node(node_entry)
                    if loaded_node:
                        self.nodes.append(loaded_node)
                except Exception as e:
                    logger.error(f"Failed to load node {node_entry.get('id')}: {e}")
                    
            logger.info(f"Registry load complete. Loaded {len(self.nodes)} nodes.")
            
        except Exception as e:
            logger.error(f"Failed to read registry file: {e}")

    def _load_node(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Load a single node based on its definition."""
        if "module" in entry:
            return self._load_code_node(entry)
        elif "path" in entry:
            return self._load_agent_node(entry)
        else:
            logger.warning(f"Node {entry.get('id')} missing 'module' or 'path'")
            return None

    def _load_agent_node(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Load an agent node from its definition folder."""
        # ... (existing implementation) ...
        path_str = entry.get("path")
        # ...

    def _load_code_node(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Load a node from its module."""
        module_path = entry.get("module")
        if not module_path:
            raise ValueError(f"Node {entry['id']} missing 'module'")
            
        # Split module and class name
        if "." not in module_path:
             raise ValueError(f"Invalid module format: {module_path}")
             
        module_name, class_name = module_path.rsplit(".", 1)
        
        try:
            module = importlib.import_module(module_name)
            node_class = getattr(module, class_name)
            
            # Instantiate to get schema
            instance = node_class(entry["id"]) if "connector" in entry.get("category", "") else node_class()
            schema = instance.model_dump() if hasattr(instance, 'model_dump') else instance.get_schema().model_dump()
            
            # Inject runner from registry if present
            if "runner" in entry:
                schema["runner"] = entry["runner"]
            
            # Ensure category is set
            schema["category"] = entry.get("category", schema.get("type", "logic"))
            
            # Preserve module path for runner
            schema["module"] = module_path
            
            return schema
            
        except ImportError as e:
            raise ImportError(f"Could not import module {module_name}: {e}")
        except AttributeError as e:
            raise AttributeError(f"Class {class_name} not found in {module_name}: {e}")

    def list_nodes(self) -> List[Dict[str, Any]]:
        return self.nodes

# Global registry instance
registry = NodeRegistry()
