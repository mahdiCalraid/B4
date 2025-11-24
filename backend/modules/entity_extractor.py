from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class EntityExtractorNode:
    """
    Extracts entities from text.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def get_schema(self):
        from schema.node import NodeSchema, NodeType
        return NodeSchema(
            id="wm-entity-extractor",
            name="Entity Extractor (WM)",
            type=NodeType.AGENT,
            description="Extracts entities from text.",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"entities": {"type": "array"}}}
        )

    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Try to get text from various sources
        context_frame = inputs.get("context_frame", {})
        text = inputs.get("text") or context_frame.get("source_text", "") or inputs.get("input")
        
        if not text:
            logger.warning("EntityExtractorNode received no text input")
            return {"entities": [], "text": ""}
            
        logger.info(f"EntityExtractor processing text: {text}")
        
        # Simple mock extraction for now - can be upgraded to use AI Agent
        entities = []
        # Basic keyword matching for demo purposes
        keywords = ["Elon Musk", "Mars", "AI", "SpaceX", "Google", "Apple"]
        for keyword in keywords:
            if keyword.lower() in text.lower():
                entities.append({
                    "name": keyword,
                    "type": "Entity", # Placeholder type
                    "confidence": 0.9
                })
            
        return {
            "entities": entities,
            "text": text,
            "context_frame": context_frame
        }
