from typing import Dict, Any, List
import re
from .base import BaseNode
from ..schema import NodeSchema, NodeType, NodeConfig

class PatternFilterNode(BaseNode):
    """
    Stage 1: ATTENTION FILTER
    Generic pattern-based filter node.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("pattern_filter", config)
        self.patterns = self.config.get("patterns", [])

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            id="wm-pattern-filter",
            name="Pattern Filter (WM)",
            type=NodeType.LOGIC,
            description="Filters input based on regex patterns.",
            icon="filter",
            color="#ef4444",
            config_schema=[
                NodeConfig(
                    name="patterns",
                    type="list",
                    label="Regex Patterns",
                    description="List of regex patterns to match against.",
                    required=True
                )
            ],
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"should_process": {"type": "boolean"}}}
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        if not text:
            # Fallback for testing/manual triggers
            text = self.config.get("fallback_text", "")
            
        if not text:
            return {
                "should_process": False,
                "relevance_score": 0.0,
                "skip_reason": "Empty text"
            }

        relevance_score = 0.0
        matches = []
        
        # Use configured patterns, or default to empty list (fail-safe)
        patterns = self.patterns
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                relevance_score += 0.2
                matches.append(pattern)
        
        relevance_score = min(relevance_score, 1.0)
        should_process = relevance_score >= 0.2

        return {
            "should_process": should_process,
            "relevance_score": relevance_score,
            "detected_patterns": matches,
            "text": text, # Pass through
            "skip_reason": None if should_process else "Low relevance"
        }
