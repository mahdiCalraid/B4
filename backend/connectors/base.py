from abc import ABC, abstractmethod
from typing import Dict, Any, List
from schema.node import NodeSchema, NodeType, NodeConfig

class BaseConnector(ABC):
    """Base class for external data connectors."""
    
    def __init__(self, connector_id: str):
        self.connector_id = connector_id
        
    @abstractmethod
    def get_schema(self) -> NodeSchema:
        """Return the node schema for this connector."""
        pass
        
    @abstractmethod
    async def execute(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the connector action."""
        pass

class TwitterConnector(BaseConnector):
    """Mock Twitter Connector."""
    
    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            id="connector-twitter",
            name="X (Twitter)",
            type=NodeType.CONNECTOR,
            description="Extract data from X/Twitter",
            icon="twitter",
            color="#000000",
            config_schema=[
                NodeConfig(
                    name="operation",
                    type="select",
                    label="Operation",
                    options=["search", "user_timeline", "trends"],
                    default="search"
                ),
                NodeConfig(
                    name="limit",
                    type="number",
                    label="Limit",
                    default=10
                )
            ],
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query or username"}
                }
            },
            output_schema={
                "type": "array",
                "items": {"type": "object", "description": "Tweet object"}
            },
            tags=["social", "data"]
        )

    async def execute(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"data": [{"text": "Mock tweet", "author": "user"}]}
