"""Base AI agent class with structured output support."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel
import json


class BaseAIAgent(ABC):
    """
    Abstract base class for all AI agents.

    Provides common interface for different LLM providers
    with support for structured output using Pydantic models.
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.provider = self.__class__.__name__.replace("Agent", "").lower()

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output using Pydantic model.

        Args:
            prompt: User prompt
            response_model: Pydantic model class for response structure
            system_prompt: Optional system instruction
            **kwargs: Additional provider-specific parameters

        Returns:
            Instance of response_model with generated data
        """
        pass

    def _get_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Get JSON schema from Pydantic model."""
        return model.model_json_schema()

    def _format_schema_for_prompt(self, model: Type[BaseModel]) -> str:
        """Format schema as string for prompt injection."""
        schema = self._get_schema(model)
        return json.dumps(schema, indent=2)

    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Generate with automatic retry on failure."""
        last_error = None

        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    continue

        raise last_error

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "provider": self.provider,
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
