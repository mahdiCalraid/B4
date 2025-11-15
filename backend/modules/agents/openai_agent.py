"""OpenAI AI agent."""

import os
import json
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel
from openai import AsyncOpenAI

from .base_ai_agent import BaseAIAgent


class OpenAIAgent(BaseAIAgent):
    """
    OpenAI AI agent with structured output support.

    Supports models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        super().__init__(model_name, api_key, temperature, max_tokens)

        # Get API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion with OpenAI."""

        messages = []

        # Add system message
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user message
        messages.append({"role": "user", "content": prompt})

        # Generate
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens)
        )

        return response.choices[0].message.content

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """Generate structured output using OpenAI's function calling."""

        messages = []

        # Add system message
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user message
        messages.append({"role": "user", "content": prompt})

        # Get schema
        schema = self._get_schema(response_model)

        # Convert to OpenAI function schema
        function_schema = {
            "name": "generate_response",
            "description": f"Generate a structured response",
            "parameters": schema
        }

        # Generate with function calling
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            functions=[function_schema],
            function_call={"name": "generate_response"},
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens)
        )

        # Parse function call response
        function_call = response.choices[0].message.function_call
        arguments = json.loads(function_call.arguments)

        return response_model(**arguments)

    def get_info(self) -> Dict[str, Any]:
        """Get OpenAI agent info."""
        info = super().get_info()
        info["provider"] = "openai"
        info["supports_structured"] = True
        info["supports_function_calling"] = True
        return info
