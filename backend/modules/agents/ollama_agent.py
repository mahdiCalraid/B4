"""Ollama local AI agent."""

import os
import json
import aiohttp
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel

from .base_ai_agent import BaseAIAgent


class OllamaAgent(BaseAIAgent):
    """
    Ollama local AI agent with structured output support.

    Supports models: llama3.2, qwen2.5, gemma2, etc.
    Requires Ollama running locally.
    """

    def __init__(
        self,
        model_name: str = "llama3.2",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        base_url: str = "http://localhost:11434"
    ):
        super().__init__(model_name, api_key, temperature, max_tokens)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion with Ollama."""

        # Prepare payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens)
            }
        }

        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        # Make request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")

                result = await response.json()
                return result.get("response", "")

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
        structured_prompt = f"""You are a helpful assistant that responds with valid JSON.

Schema to follow:
{schema_str}

User request: {prompt}

Respond ONLY with valid JSON matching the schema above. Do not include any explanation or markdown formatting."""

        # Generate
        full_system = system_prompt or "You are a helpful assistant."
        response_text = await self.generate(
            structured_prompt,
            system_prompt=full_system,
            **kwargs
        )

        # Parse and validate
        try:
            # Clean the response
            text = response_text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()

            # Parse JSON
            json_response = json.loads(text)
            return response_model(**json_response)

        except Exception as e:
            # If parsing fails, try to find JSON in the text
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_response = json.loads(json_match.group())
                return response_model(**json_response)

            raise ValueError(f"Failed to parse structured output: {e}\nResponse: {text}")

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    return response.status == 200
        except:
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get Ollama agent info."""
        info = super().get_info()
        info["provider"] = "ollama"
        info["base_url"] = self.base_url
        info["supports_structured"] = True
        info["local"] = True
        info["cost"] = "free"
        return info
