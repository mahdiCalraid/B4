"""Unified AI Chat Module with multi-provider support."""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from modules.base import BaseModule, ModuleType
from modules.agents.gemini_agent import GeminiAgent
from modules.agents.openai_agent import OpenAIAgent
from modules.agents.groq_agent import GroqAgent
from modules.agents.ollama_agent import OllamaAgent


# Example structured output model
class ChatResponse(BaseModel):
    """Structured chat response."""
    answer: str = Field(description="The main answer to the user's question")
    confidence: float = Field(description="Confidence score 0-1", ge=0, le=1)
    sources: list[str] = Field(default_factory=list, description="Sources or reasoning")


class AIChatModule(BaseModule):
    """
    Unified AI Chat Module with multi-provider routing.

    Supports: Gemini, OpenAI, Groq, Ollama (fallback)

    Priority order (configurable):
    1. Gemini (default - fast and free tier)
    2. OpenAI (if specified or Gemini fails)
    3. Groq (fast inference)
    4. Ollama (local fallback)
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.INTERACTIVE
        self.version = "2.0.0"

        # Initialize agents (lazy loading)
        self._agents = {}
        self._default_provider = "gemini"

    def _get_agent(self, provider: str):
        """Get or create agent for provider."""
        if provider in self._agents:
            return self._agents[provider]

        try:
            if provider == "gemini":
                agent = GeminiAgent(model_name="gemini-2.0-flash-exp")
            elif provider == "openai":
                agent = OpenAIAgent(model_name="gpt-4o-mini")
            elif provider == "groq":
                agent = GroqAgent(model_name="llama-3.3-70b-versatile")
            elif provider == "ollama":
                agent = OllamaAgent(model_name="llama3.2")
            else:
                raise ValueError(f"Unknown provider: {provider}")

            self._agents[provider] = agent
            return agent

        except Exception as e:
            print(f"Failed to initialize {provider} agent: {e}")
            return None

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process chat request with intelligent provider routing.

        Args:
            input_data: {
                "text": str (required),
                "user_id": str (optional),
                "provider": str (optional: gemini|openai|groq|ollama),
                "model": str (optional: specific model name),
                "structured": bool (optional: use structured output),
                "system_prompt": str (optional),
                "temperature": float (optional),
                "max_tokens": int (optional)
            }

        Returns:
            {
                "response": str,
                "provider": str,
                "model": str,
                "confidence": float,
                "processing_time_ms": int,
                ...
            }
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
        provider = input_data.get("provider", self._default_provider).lower()
        use_structured = input_data.get("structured", False)
        system_prompt = input_data.get("system_prompt")
        temperature = input_data.get("temperature")
        max_tokens = input_data.get("max_tokens")

        # Build kwargs
        kwargs = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        # Provider priority list (fallback order)
        providers_to_try = [provider]

        # Add fallbacks
        if provider != "gemini":
            providers_to_try.append("gemini")
        if provider != "openai":
            providers_to_try.append("openai")
        if provider != "groq":
            providers_to_try.append("groq")
        if provider != "ollama":
            providers_to_try.append("ollama")

        # Try providers in order
        last_error = None
        for current_provider in providers_to_try:
            try:
                agent = self._get_agent(current_provider)
                if not agent:
                    continue

                # Check if Ollama is available before trying
                if current_provider == "ollama":
                    if not await agent.is_available():
                        print("Ollama not available, skipping")
                        continue

                # Generate response
                if use_structured:
                    result = await agent.generate_structured(
                        text,
                        ChatResponse,
                        system_prompt=system_prompt,
                        **kwargs
                    )
                    response_text = result.answer
                    confidence = result.confidence
                else:
                    response_text = await agent.generate(
                        text,
                        system_prompt=system_prompt,
                        **kwargs
                    )
                    confidence = 0.9

                # Success!
                return {
                    "response": response_text,
                    "provider": current_provider,
                    "model": agent.model_name,
                    "confidence": confidence,
                    "structured": use_structured,
                    **self._get_processing_metadata(start_time)
                }

            except Exception as e:
                last_error = str(e)
                print(f"Provider {current_provider} failed: {e}")
                continue

        # All providers failed
        return {
            "error": f"All providers failed. Last error: {last_error}",
            "confidence": 0.0,
            "providers_tried": providers_to_try,
            **self._get_processing_metadata(start_time)
        }

    def get_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.module_type.value,
            "description": "Unified AI chat with multi-provider support (Gemini, OpenAI, Groq, Ollama)",
            "supported_providers": ["gemini", "openai", "groq", "ollama"],
            "default_provider": self._default_provider,
            "supports_structured_output": True
        }
