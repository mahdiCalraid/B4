from typing import Dict, Any
from .base import BaseNodeRunner, ExecutionContext
import importlib
import logging

logger = logging.getLogger(__name__)

class WorldModelRunner(BaseNodeRunner):
    """
    Executes World Model nodes by dynamically loading their class.
    Requires '_node_def' to be injected into config by the engine.
    """
    
    async def run(self, config: Dict[str, Any], inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        node_def = config.get("_node_def")
        if not node_def:
            raise ValueError("WorldModelRunner requires '_node_def' in config")
            
        module_path = node_def.get("module")
        if not module_path:
            raise ValueError(f"Node definition {node_def.get('id')} missing 'module'")
            
        # Load the node class
        try:
            # Expected format: package.module.ClassName
            module_name, class_name = module_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            node_class = getattr(module, class_name)
            
            # Instantiate with config (stripped of internal keys)
            clean_config = {k: v for k, v in config.items() if not k.startswith("_")}
            node_instance = node_class(config=clean_config)
            
            # Execute process
            logger.info(f"Executing {class_name} with inputs: {inputs.keys()}")
            return await node_instance.process(inputs)
            
        except Exception as e:
            logger.error(f"Failed to execute world model node: {e}")
            raise e
