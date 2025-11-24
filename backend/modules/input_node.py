"""Input Node - Allows users to provide text input to workflows."""

from typing import Dict, Any
from pydantic import BaseModel, Field


class InputNodeSchema(BaseModel):
    """Schema for the Input Node."""
    id: str = "input-text"
    name: str = "Text Input"
    category: str = "trigger"
    description: str = "Allows user to input text to start a workflow"
    version: str = "1.0.0"
    icon: str = "message-square"
    color: str = "#10b981"
    tags: list = Field(default_factory=lambda: ["input", "trigger"])
    
    config_schema: list = Field(default_factory=lambda: [
        {
            "name": "placeholder",
            "type": "string",
            "label": "Placeholder Text",
            "description": "Placeholder text shown in the input field",
            "default": "Enter your text here..."
        },
        {
            "name": "default_text",
            "type": "string",
            "label": "Default Text",
            "description": "Pre-filled text in the input field",
            "default": ""
        }
    ])
    
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    
    output_schema: Dict[str, Any] = Field(default_factory=lambda: {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The user-provided text input"
            }
        }
    })


class InputNode:
    """Input node that outputs user-provided text."""
    
    def __init__(self):
        pass
    
    def get_schema(self):
        """Return the node schema."""
        return InputNodeSchema()
