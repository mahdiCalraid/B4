"""Simple chat agent module."""

from typing import Dict, Any
from datetime import datetime
from modules.base import BaseModule, ModuleType


class ChatAgentModule(BaseModule):
    """
    Simple conversational AI agent.

    Provides basic chat functionality for testing the module system.
    Can be enhanced with actual AI models later.
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.INTERACTIVE
        self.version = "1.0.0"

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a chat message and return a response.

        Args:
            input_data: Dictionary with 'text' and optional 'user_id'

        Returns:
            Dictionary with response and metadata
        """
        start_time = datetime.now()

        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return {
                "error": error,
                "confidence": 0.0,
                **self._get_processing_metadata(start_time)
            }

        text = input_data.get("text", "")
        user_id = input_data.get("user_id", "anonymous")

        # Simple pattern-based responses
        response = self._generate_response(text, user_id)

        return {
            "response": response,
            "confidence": 0.85,
            "intent": self._detect_intent(text),
            **self._get_processing_metadata(start_time)
        }

    def _generate_response(self, text: str, user_id: str) -> str:
        """Generate a simple response based on input text."""
        text_lower = text.lower()

        # Greeting responses
        if any(word in text_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! How can I help you today?"

        # Help responses
        if any(word in text_lower for word in ["help", "what can you do"]):
            return (
                "I'm a simple chat agent. I can:\n"
                "- Answer basic questions\n"
                "- Help you understand the system\n"
                "- Route you to specialized modules\n\n"
                "Try asking me to 'analyze' something or 'classify' content!"
            )

        # Analysis routing
        if any(word in text_lower for word in ["analyze", "analysis"]):
            return (
                "For analysis, you should use the AnalyzerModule. "
                "You can specify it by adding 'module': 'AnalyzerModule' to your request."
            )

        # Default response
        return (
            "I received your message. I'm a simple chat agent for testing. "
            "Try asking for 'help' to see what I can do!"
        )

    def _detect_intent(self, text: str) -> str:
        """Detect user intent from text."""
        text_lower = text.lower()

        if any(word in text_lower for word in ["hello", "hi", "hey"]):
            return "greeting"

        if any(word in text_lower for word in ["help", "what can you do"]):
            return "help_request"

        if any(word in text_lower for word in ["analyze", "analysis"]):
            return "analysis_request"

        if "?" in text:
            return "question"

        return "statement"
