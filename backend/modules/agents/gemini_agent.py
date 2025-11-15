"""Google Gemini AI agent."""

import os
import json
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel
import google.generativeai as genai

from .base_ai_agent import BaseAIAgent


class GeminiAgent(BaseAIAgent):
    """
    Google Gemini AI agent with structured output support.

    Supports models: gemini-2.0-flash-exp, gemini-1.5-pro, gemini-1.5-flash
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        super().__init__(model_name, api_key, temperature, max_tokens)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("gemeni_key")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion with Gemini."""

        # Combine system and user prompts
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"

        # Generate
        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=kwargs.get("temperature", self.temperature),
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
        )

        return response.text

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """Generate structured output using Gemini's JSON mode."""

        # Get schema
        schema = self._get_schema(response_model)

        # Create prompt with schema
        schema_str = json.dumps(schema, indent=2)
        structured_prompt = f"""{system_prompt or "You are a helpful assistant."}

Generate a JSON response that matches this schema:
{schema_str}

User request: {prompt}

Respond ONLY with valid JSON matching the schema above."""

        # Generate with JSON mode
        response = self.model.generate_content(
            structured_prompt,
            generation_config=genai.GenerationConfig(
                temperature=kwargs.get("temperature", self.temperature),
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                response_mime_type="application/json"
            )
        )

        # Parse and validate
        try:
            json_response = json.loads(response.text)
            return response_model(**json_response)
        except Exception as e:
            # Fallback: try to extract JSON from text
            text = response.text.strip()
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()

            json_response = json.loads(text)
            return response_model(**json_response)

    def get_info(self) -> Dict[str, Any]:
        """Get Gemini agent info."""
        info = super().get_info()
        info["provider"] = "gemini"
        info["supports_structured"] = True
        info["supports_json_mode"] = True
        return info
