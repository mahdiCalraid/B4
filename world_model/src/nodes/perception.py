from typing import Dict, Any, List
from datetime import datetime
from .base import BaseNode
from ..schema import NodeSchema, NodeType

class ContextBuilderNode(BaseNode):
    """
    Stage 2: PERCEPTION LAYER
    Establish contextual understanding before extraction.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("context_builder", config)

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            id="wm-context-builder",
            name="Context Builder (WM)",
            type=NodeType.AGENT,
            description="Builds context from input and memory.",
            icon="map",
            color="#3b82f6"
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        
        context_frame = {
            "source_context": {
                "type": "unknown",
                "platform": "unknown"
            },
            "temporal_context": {
                "processed_at": datetime.utcnow().isoformat(),
                "references": []
            },
            "domain_context": input_data.get("detected_patterns", [])
        }

        memory_hints = {
            "similar_contexts": [],
            "related_entities": []
        }
        
        return {
            "context_frame": context_frame,
            "memory_hints": memory_hints,
            "text": text # Pass through
        }
