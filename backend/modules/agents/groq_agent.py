"""Groq AI agent."""

import os
import json
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel
from groq import AsyncGroq

from .base_ai_agent import BaseAIAgent


class GroqAgent(BaseAIAgent):
    """
    Groq AI agent with structured output support.

    Supports models: llama-3.3-70b-versatile, mixtral-8x7b-32768
    """

    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        super().__init__(model_name, api_key, temperature, max_tokens)

        # Get API key
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        # Initialize Groq client
        self.client = AsyncGroq(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion with Groq."""

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
        """Generate structured output using JSON mode."""

        # Get schema
        schema = self._get_schema(response_model)
        schema_str = json.dumps(schema, indent=2)

        # Create structured prompt
        structured_system = f"""{system_prompt or "You are a helpful assistant."}

You must respond with valid JSON that matches this schema:
{schema_str}"""

        messages = [
            {"role": "system", "content": structured_system},
            {"role": "user", "content": prompt}
        ]

        # Generate with JSON mode
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            response_format={"type": "json_object"}
        )

        # Parse and validate
        content = response.choices[0].message.content

        try:
            json_response = json.loads(content)
            return response_model(**json_response)
        except Exception as e:
            # Fallback: try to extract JSON
            text = content.strip()
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()

            json_response = json.loads(text)
            return response_model(**json_response)

    def get_info(self) -> Dict[str, Any]:
        """Get Groq agent info."""
        info = super().get_info()
        info["provider"] = "groq"
        info["supports_structured"] = True
        info["supports_json_mode"] = True
        return info
