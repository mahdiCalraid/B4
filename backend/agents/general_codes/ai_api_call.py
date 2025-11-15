"""AI API calling utilities."""

from typing import Dict, Any, Optional, Type
from pydantic import BaseModel

from modules.agents.base_ai_agent import BaseAIAgent


async def call_ai_api(
    provider: BaseAIAgent,
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    Call AI API for text generation.

    Args:
        provider: AI provider instance
        prompt: User prompt
        system_prompt: Optional system instruction
        **kwargs: Additional provider-specific parameters

    Returns:
        Generated text
    """
    return await provider.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        **kwargs
    )


async def call_ai_structured(
    provider: BaseAIAgent,
    prompt: str,
    response_model: Type[BaseModel],
    system_prompt: Optional[str] = None,
    **kwargs
) -> BaseModel:
    """
    Call AI API for structured output generation.

    Args:
        provider: AI provider instance
        prompt: User prompt
        response_model: Pydantic model for response structure
        system_prompt: Optional system instruction
        **kwargs: Additional provider-specific parameters

    Returns:
        Pydantic model instance with generated data
    """
    return await provider.generate_structured(
        prompt=prompt,
        response_model=response_model,
        system_prompt=system_prompt,
        **kwargs
    )


async def call_with_fallback(
    providers: list[BaseAIAgent],
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    Call AI API with fallback to other providers on failure.

    Args:
        providers: List of AI providers to try in order
        prompt: User prompt
        system_prompt: Optional system instruction
        **kwargs: Additional parameters

    Returns:
        Generated text from first successful provider

    Raises:
        Exception: If all providers fail
    """
    last_error = None

    for provider in providers:
        try:
            return await call_ai_api(
                provider=provider,
                prompt=prompt,
                system_prompt=system_prompt,
                **kwargs
            )
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"All providers failed. Last error: {last_error}")
