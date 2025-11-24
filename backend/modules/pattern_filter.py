from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

class PatternFilterNode:
    """
    Filters input text based on configured patterns.
    Currently uses Regex, but can be upgraded to use AI for semantic matching.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.patterns = self.config.get("patterns", [])
        if not self.patterns and "config" in self.config:
             self.patterns = self.config["config"].get("patterns", [])

    def get_schema(self):
        from schema.node import NodeSchema, NodeType, NodeConfig
        return NodeSchema(
            id="wm-pattern-filter",
            name="Pattern Filter (WM)",
            type=NodeType.LOGIC,
            description="Filters input based on regex patterns.",
            config_schema=[
                NodeConfig(name="patterns", type="list", label="Patterns", description="List of regex patterns")
            ],
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"matches": {"type": "array"}, "is_match": {"type": "boolean"}}}
        )

    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Handle various input keys
        text = inputs.get("text") or inputs.get("input") or inputs.get("input_data", {}).get("text")
        
        if not text:
            logger.warning("PatternFilterNode received no text input")
            return {"matches": [], "is_match": False, "text": ""}

        logger.info(f"PatternFilter processing text: '{text}' against {len(self.patterns)} patterns")
        
        matches = []
        for pattern in self.patterns:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)
            except re.error:
                logger.error(f"Invalid regex pattern: {pattern}")
        
        result = {
            "matches": matches,
            "is_match": len(matches) > 0,
            "text": text,
            # Pass through other metadata if needed
            "metadata": inputs.get("metadata", {})
        }
        
        logger.info(f"PatternFilter result: {result['is_match']} ({len(matches)} matches)")
        return result
