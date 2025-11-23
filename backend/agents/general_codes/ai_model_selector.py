"""
AI Model Selection and Management.

This module provides a unified interface for selecting and using different AI models
with support for structured output across all providers.
"""

from typing import Dict, Any, Optional, Type, List
from pydantic import BaseModel
import os

from modules.agents.base_ai_agent import BaseAIAgent
from modules.agents.gemini_agent import GeminiAgent
from modules.agents.openai_agent import OpenAIAgent
# from modules.agents.groq_agent import GroqAgent  # Temporarily disabled - missing groq package
from modules.agents.ollama_agent import OllamaAgent
from modules.agents.deepinfra_agent import DeepInfraAgent

# Placeholder for GroqAgent
class GroqAgent:
    """Placeholder for GroqAgent when groq package is not installed."""
    pass


# Model registry with provider mapping
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Gemini models
    "gemini-2.0-flash-exp": {
        "provider": "gemini",
        "name": "gemini-2.0-flash-exp",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 1000000,
        "description": "Latest Gemini 2.0 Flash experimental - fast and powerful"
    },
    "gemini-2.0-flash": {
        "provider": "gemini",
        "name": "gemini-2.0-flash",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 1000000,
        "description": "Gemini 2.0 Flash - stable version"
    },
    "gemini-1.5-pro": {
        "provider": "gemini",
        "name": "gemini-1.5-pro",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 2000000,
        "description": "Gemini 1.5 Pro - highest quality"
    },
    "gemini-1.5-flash": {
        "provider": "gemini",
        "name": "gemini-1.5-flash",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 1000000,
        "description": "Gemini 1.5 Flash - balanced performance"
    },

    # OpenAI models
    "gpt-4o": {
        "provider": "openai",
        "name": "gpt-4o",
        "supports_structured": True,
        "supports_function_calling": True,
        "context_window": 128000,
        "description": "GPT-4 Omni - multimodal flagship"
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "name": "gpt-4o-mini",
        "supports_structured": True,
        "supports_function_calling": True,
        "context_window": 128000,
        "description": "GPT-4 Omni Mini - affordable and fast"
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "name": "gpt-4-turbo",
        "supports_structured": True,
        "supports_function_calling": True,
        "context_window": 128000,
        "description": "GPT-4 Turbo - high performance"
    },
    "gpt-4-turbo-2024-04-09": {
        "provider": "openai",
        "name": "gpt-4-turbo-2024-04-09",
        "supports_structured": True,
        "supports_function_calling": True,
        "context_window": 128000,
        "description": "GPT-4 Turbo April 2024 snapshot"
    },
    "gpt-3.5-turbo": {
        "provider": "openai",
        "name": "gpt-3.5-turbo",
        "supports_structured": True,
        "supports_function_calling": True,
        "context_window": 16385,
        "description": "GPT-3.5 Turbo - cost-effective"
    },

    # Groq models (ultra-fast inference)
    "llama-3.3-70b-versatile": {
        "provider": "groq",
        "name": "llama-3.3-70b-versatile",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 8192,
        "description": "LLaMA 3.3 70B on Groq - ultra-fast inference"
    },
    "llama-3.3-70b-specdec": {
        "provider": "groq",
        "name": "llama-3.3-70b-specdec",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 8192,
        "description": "LLaMA 3.3 70B with speculative decoding"
    },
    "llama-3.1-70b-versatile": {
        "provider": "groq",
        "name": "llama-3.1-70b-versatile",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 131072,
        "description": "LLaMA 3.1 70B - large context"
    },
    "llama-3.1-8b-instant": {
        "provider": "groq",
        "name": "llama-3.1-8b-instant",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 131072,
        "description": "LLaMA 3.1 8B - instant responses"
    },
    "mixtral-8x7b-32768": {
        "provider": "groq",
        "name": "mixtral-8x7b-32768",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 32768,
        "description": "Mixtral 8x7B MoE - efficient and powerful"
    },

    # Ollama models (local)
    "llama3.2": {
        "provider": "ollama",
        "name": "llama3.2",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 128000,
        "description": "LLaMA 3.2 local - privacy-first"
    },
    "llama3.1": {
        "provider": "ollama",
        "name": "llama3.1",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 128000,
        "description": "LLaMA 3.1 local - high quality"
    },
    "gemma2": {
        "provider": "ollama",
        "name": "gemma2",
        "supports_structured": True,
        "supports_json_mode": True,
        "context_window": 8192,
        "description": "Gemma 2 local - Google's open model"
    },

    # DeepInfra models
    "gpt-oss-20b": {
        "provider": "deepinfra",
        "name": "openai/gpt-oss-20b",
        "supports_structured": True,
        "supports_json_mode": False,  # This model doesn't support response_format json_object
        "context_window": 8192,
        "description": "GPT-OSS 20B - Open-source 21B param MoE model via DeepInfra"
    },
    "openai/gpt-oss-20b": {
        "provider": "deepinfra",
        "name": "openai/gpt-oss-20b",
        "supports_structured": True,
        "supports_json_mode": False,  # This model doesn't support response_format json_object
        "context_window": 8192,
        "description": "GPT-OSS 20B - Open-source 21B param MoE model via DeepInfra"
    },
}

# Aliases for convenience
MODEL_ALIASES = {
    # GPT aliases
    "gpt4": "gpt-4o",
    "gpt4o": "gpt-4o",
    "gpt4-mini": "gpt-4o-mini",
    # Gemini aliases
    "gemini": "gemini-2.0-flash-exp",
    "gemini-flash": "gemini-2.0-flash",
    "gemini-pro": "gemini-1.5-pro",
    # LLaMA aliases
    "llama": "llama-3.3-70b-versatile",
    "llama3.3": "llama-3.3-70b-versatile",
    # Other aliases
    "mixtral": "mixtral-8x7b-32768",
}


class AIModelSelector:
    """
    Unified interface for selecting and using AI models.

    Handles model selection, provider instantiation, and structured output
    generation across different AI providers.
    """

    def __init__(self, default_model: str = "gemini-2.0-flash-exp"):
        """
        Initialize model selector.

        Args:
            default_model: Default model to use if none specified
        """
        self.default_model = default_model
        self._provider_cache: Dict[str, BaseAIAgent] = {}

    def _resolve_model_name(self, model: Optional[str]) -> str:
        """
        Resolve model name from alias or return actual name.

        Args:
            model: Model name or alias

        Returns:
            Resolved model name
        """
        if not model:
            return self.default_model

        # Check if it's an alias
        if model in MODEL_ALIASES:
            return MODEL_ALIASES[model]

        # Check if it's a valid model
        if model in MODEL_REGISTRY:
            return model

        # If not found, try case-insensitive search
        model_lower = model.lower()
        for key in MODEL_REGISTRY:
            if key.lower() == model_lower:
                return key

        # If still not found, return default
        print(f"⚠️  Model '{model}' not found, using default: {self.default_model}")
        return self.default_model

    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a model.

        Args:
            model: Model name or alias

        Returns:
            Model metadata
        """
        model_name = self._resolve_model_name(model)

        if model_name not in MODEL_REGISTRY:
            raise ValueError(f"Model not found: {model_name}")

        info = MODEL_REGISTRY[model_name].copy()
        info["resolved_name"] = model_name

        return info

    def list_models(
        self,
        provider: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        List all available models.

        Args:
            provider: Filter by provider (gemini, openai, groq, ollama)

        Returns:
            Dictionary of model information
        """
        if provider:
            return {
                name: info
                for name, info in MODEL_REGISTRY.items()
                if info["provider"] == provider.lower()
            }

        return MODEL_REGISTRY.copy()

    def _get_provider_instance(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> BaseAIAgent:
        """
        Get or create provider instance for a model.

        Args:
            model_name: Resolved model name
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Provider instance
        """
        cache_key = f"{model_name}:{temperature}:{max_tokens}"

        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]

        model_info = MODEL_REGISTRY[model_name]
        provider_type = model_info["provider"]

        # Get the actual model name for the provider (e.g., "openai/gpt-oss-20b" for DeepInfra)
        actual_model_name = model_info["name"]

        # Create provider instance
        if provider_type == "gemini":
            provider = GeminiAgent(
                model_name=actual_model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider_type == "openai":
            provider = OpenAIAgent(
                model_name=actual_model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider_type == "groq":
            provider = GroqAgent(
                model_name=actual_model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider_type == "ollama":
            provider = OllamaAgent(
                model_name=actual_model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider_type == "deepinfra":
            provider = DeepInfraAgent(
                model_name=actual_model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"Unknown provider: {provider_type}")

        # Cache and return
        self._provider_cache[cache_key] = provider
        return provider

    async def generate(
        self,
        input_text: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Generate text response.

        Args:
            input_text: Input text/prompt
            model: Model name or alias
            system_prompt: System prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        model_name = self._resolve_model_name(model)
        provider = self._get_provider_instance(model_name, temperature, max_tokens)

        return await provider.generate(
            prompt=input_text,
            system_prompt=system_prompt,
            **kwargs
        )

    async def generate_structured(
        self,
        input_text: str,
        output_schema: Type[BaseModel],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output.

        Args:
            input_text: Input text/prompt
            output_schema: Pydantic model for output structure
            model: Model name or alias
            system_prompt: System prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Pydantic model instance with structured data
        """
        model_name = self._resolve_model_name(model)
        provider = self._get_provider_instance(model_name, temperature, max_tokens)

        return await provider.generate_structured(
            prompt=input_text,
            response_model=output_schema,
            system_prompt=system_prompt,
            **kwargs
        )


# Global selector instance
_global_selector = None


def get_model_selector() -> AIModelSelector:
    """Get or create global model selector instance."""
    global _global_selector
    if _global_selector is None:
        _global_selector = AIModelSelector()
    return _global_selector


def list_available_models(provider: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """List all available models."""
    selector = get_model_selector()
    return selector.list_models(provider=provider)


def get_model_info(model: str) -> Dict[str, Any]:
    """Get information about a specific model."""
    selector = get_model_selector()
    return selector.get_model_info(model)
