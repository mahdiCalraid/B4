from abc import ABC, abstractmethod
from typing import Dict, Any
from schema.node import NodeSchema, NodeType, NodeConfig

class BaseLogic(ABC):
    """Base class for logic nodes."""
    
    @abstractmethod
    def get_schema(self) -> NodeSchema:
        pass

class RouterNode(BaseLogic):
    """Simple Router Node."""
    
    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            id="logic-router",
            name="Router",
            type=NodeType.LOGIC,
            description="Route execution based on condition",
            icon="git-branch",
            color="#f59e0b", # amber-500
            config_schema=[
                NodeConfig(
                    name="condition",
                    type="string",
                    label="Condition",
                    description="Python expression (e.g. input.value > 10)"
                )
            ],
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            tags=["logic", "flow"]
        )
