from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from ..schema import NodeSchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseNode(ABC):
    """Base class for all memory workflow nodes."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"node.{name}")

    @abstractmethod
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for this node."""
        pass

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return the result.
        """
        pass
