from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class NodeType(Enum):
    AGENT = "agent"           # AI Agent (LLM)
    CONNECTOR = "connector"   # External API (Twitter, BQ)
    LOGIC = "logic"           # Router, Filter, Merge
    TRIGGER = "trigger"       # Webhook, Schedule

class NodeConfig(BaseModel):
    """Configuration parameter definition for a node."""
    name: str
    type: str  # string, number, boolean, select, secret
    label: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    options: Optional[List[str]] = None  # For select type

class NodeSchema(BaseModel):
    """Standard definition of a computational node."""
    id: str
    name: str
    type: NodeType
    description: str
    version: str = "1.0.0"
    
    # Visuals
    icon: str = "box"  # Lucide icon name
    color: str = "#ffffff"
    
    # Configuration Schema (Static parameters configured in UI)
    config_schema: List[NodeConfig] = Field(default_factory=list)
    
    # I/O Contract (JSON Schema)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
