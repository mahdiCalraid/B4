from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextBuilderNode:
    """
    Builds context from input text and potentially other sources.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def get_schema(self):
        from schema.node import NodeSchema, NodeType
        return NodeSchema(
            id="wm-context-builder",
            name="Context Builder (WM)",
            type=NodeType.AGENT,
            description="Builds context from input and memory.",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"context_frame": {"type": "object"}}}
        )

    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Handle various input keys
        text = inputs.get("text") or inputs.get("input") or inputs.get("input_data", {}).get("text")
        
        # Also check if input comes from Pattern Filter
        if not text and "text" in inputs:
            text = inputs["text"]
            
        if not text:
            logger.warning("ContextBuilderNode received no text input")
            return {"context_frame": {}, "text": ""}
            
        logger.info(f"ContextBuilder processing text: {text}")
        
        # Simple context building for now
        context_frame = {
            "source_text": text,
            "derived_context": "Derived context placeholder",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "context_frame": context_frame,
            "text": text
        }
