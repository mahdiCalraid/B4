from typing import Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PatternFilterNode:
    """
    AI-powered Interest Detector that identifies meaningful content across 14 categories.
    Uses the interest_detector agent for semantic understanding.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agent = None
        self._agent_loaded = False
        
    def _load_agent(self):
        """Lazy load the interest_detector agent."""
        if self._agent_loaded:
            return
            
        try:
            from agents.agent_loader import get_loader
            loader = get_loader()
            self.agent = loader.load_agent("interest_detector", provider="gemini")
            self._agent_loaded = True
            logger.info("✅ Loaded interest_detector agent")
        except Exception as e:
            logger.error(f"Failed to load interest_detector agent: {e}")
            raise

    def get_schema(self):
        from schema.node import NodeSchema, NodeType, NodeConfig
        return NodeSchema(
            id="wm-pattern-filter",
            name="Pattern Filter (WM)",
            type=NodeType.AGENT,
            description="AI-powered interest detection across 14 categories of personal relevance",
            config_schema=[],
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={
                "type": "object", 
                "properties": {
                    "interesting": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "interesting_field": {"type": "string"},
                                "interesting_score": {"type": "integer"},
                                "reason": {"type": "string"},
                                "text_snippet": {"type": "string"}
                            }
                        }
                    }
                }
            }
        )

    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process input text through the interest_detector agent."""
        # Handle various input keys
        text = inputs.get("text") or inputs.get("input") or inputs.get("input_data", {}).get("text")
        
        if not text:
            logger.warning("PatternFilterNode received no text input")
            return {
                "interesting": [],
                "text": "",
                "metadata": inputs.get("metadata", {})
            }

        logger.info(f"PatternFilter processing text: '{text[:100]}...'")
        
        # Load agent if not already loaded
        self._load_agent()
        
        try:
            # Process through AI agent
            result = await self.agent.process(
                input_data=text,
                model="gemini-2.0-flash-exp"
            )
            
            # Extract interesting items
            interesting_items = result.get("interesting", [])
            
            logger.info(f"PatternFilter detected {len(interesting_items)} interesting items")
            
            # Return result with pass-through data
            return {
                "interesting": interesting_items,
                "text": text,
                "metadata": inputs.get("metadata", {}),
                "num_interesting": len(interesting_items)
            }
            
        except Exception as e:
            logger.error(f"PatternFilter AI processing failed: {e}")
            # Return empty result on error
            return {
                "interesting": [],
                "text": text,
                "metadata": inputs.get("metadata", {}),
                "error": str(e)
            }
