"""DeepInfra AI agent."""

import os
import json
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel
from openai import AsyncOpenAI

from .base_ai_agent import BaseAIAgent


class DeepInfraAgent(BaseAIAgent):
    """
    DeepInfra AI agent with structured output support.

    Uses OpenAI-compatible API with DeepInfra endpoint.
    Supports models: openai/gpt-oss-20b, meta-llama/Meta-Llama-3.1-70B-Instruct, etc.
    """

    def __init__(
        self,
        model_name: str = "openai/gpt-oss-20b",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        super().__init__(model_name, api_key, temperature, max_tokens)

        # Get API key
        self.api_key = api_key or os.getenv("DEEPINFRA_API_KEY") or os.getenv("DEEPINFRA_TOKEN")

        if not self.api_key:
            raise ValueError("DEEPINFRA_API_KEY or DEEPINFRA_TOKEN not found in environment")

        # Initialize DeepInfra client using OpenAI-compatible interface
        # Note: We explicitly avoid passing any proxy settings
        try:
            self.client = AsyncOpenAI(
                base_url="https://api.deepinfra.com/v1/openai",
                api_key=self.api_key,
                timeout=60.0,
                max_retries=2
            )
        except TypeError:
            # Fallback for older OpenAI client versions
            self.client = AsyncOpenAI(
                base_url="https://api.deepinfra.com/v1/openai",
                api_key=self.api_key
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion with DeepInfra."""

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
        """Generate structured output using prompt engineering."""

        # Get schema
        schema = self._get_schema(response_model)
        schema_str = json.dumps(schema, indent=2)

        # Create structured prompt
        structured_system = f"""{system_prompt or "You are a helpful assistant."}

You must respond with valid JSON that matches this schema:
{schema_str}

IMPORTANT: Return ONLY valid JSON, no additional text."""

        messages = [
            {"role": "system", "content": structured_system},
            {"role": "user", "content": prompt}
        ]

        # Generate without JSON mode (not all DeepInfra models support it)
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens)
        )

        # Parse and validate
        content = response.choices[0].message.content

        try:
            json_response = json.loads(content)
            return response_model(**json_response)
        except Exception as e:
            # Fallback: try to extract JSON from text
            text = content.strip()
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()

            json_response = json.loads(text)
            return response_model(**json_response)

    def get_info(self) -> Dict[str, Any]:
        """Get DeepInfra agent info."""
        info = super().get_info()
        info["provider"] = "deepinfra"
        info["supports_structured"] = True
        info["supports_json_mode"] = False  # Model doesn't support response_format json_object
        return info
