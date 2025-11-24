from typing import Dict, Any, List
from .base import BaseNode
from ..schema import NodeSchema, NodeType

class EntityExtractorNode(BaseNode):
    """
    Stage 3.1: Entity Stream (WHO/WHAT)
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("entity_extractor", config)

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            id="wm-entity-extractor",
            name="Entity Extractor (WM)",
            type=NodeType.AGENT,
            description="Extracts entities from text.",
            icon="users",
            color="#10b981"
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        entities = []
        # Mock logic - in real world would use config to decide what models to use
        if "Elon Musk" in text:
            entities.append({"text": "Elon Musk", "type": "PERSON", "confidence": 0.99})
        if "SpaceX" in text:
            entities.append({"text": "SpaceX", "type": "ORG", "confidence": 0.99})
        if "Mars" in text:
            entities.append({"text": "Mars", "type": "LOC", "confidence": 0.99})
            
        return {"entities": entities}

class EventActionNode(BaseNode):
    """
    Stage 3.2: Event Stream (WHAT HAPPENED)
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("event_action", config)

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            id="wm-event-action",
            name="Event Action (WM)",
            type=NodeType.AGENT,
            description="Extracts events and actions.",
            icon="activity",
            color="#8b5cf6"
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        events = []
        if "said" in text or "announced" in text:
             events.append({
                 "type": "statement",
                 "description": "Someone made a statement",
                 "confidence": 0.8
             })
        return {"events": events}

class ConceptSentimentNode(BaseNode):
    """
    Stage 3.3: Idea Stream (WHAT IT MEANS)
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("concept_sentiment", config)

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            id="wm-concept-sentiment",
            name="Concept & Sentiment (WM)",
            type=NodeType.AGENT,
            description="Extracts concepts and sentiment.",
            icon="lightbulb",
            color="#f59e0b"
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "concepts": [],
            "sentiment": "neutral"
        }
