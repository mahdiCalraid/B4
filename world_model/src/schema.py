from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class NodeType(Enum):
    AGENT = "agent"
    CONNECTOR = "connector"
    LOGIC = "logic"
    TRIGGER = "trigger"

class NodeConfig(BaseModel):
    name: str
    type: str
    label: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    options: Optional[List[str]] = None

class NodeSchema(BaseModel):
    id: str
    name: str
    type: NodeType
    description: str
    version: str = "1.0.0"
    icon: str = "box"
    color: str = "#ffffff"
    config_schema: List[NodeConfig] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
