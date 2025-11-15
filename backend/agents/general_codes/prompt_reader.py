"""Prompt reading and formatting utilities."""

from pathlib import Path
from typing import Dict, Any


def read_prompt(prompt_path: Path) -> str:
    """
    Read prompt from file.

    Args:
        prompt_path: Path to prompt.txt file

    Returns:
        Prompt text
    """
    if not prompt_path.exists():
        return "You are a helpful AI assistant."

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def format_prompt(
    template: str,
    variables: Dict[str, Any]
) -> str:
    """
    Format prompt template with variables.

    Args:
        template: Prompt template with {variable} placeholders
        variables: Dictionary of variables to substitute

    Returns:
        Formatted prompt

    Example:
        template = "Extract {entity_type} from: {text}"
        variables = {"entity_type": "people", "text": "John went to NYC"}
        result = "Extract people from: John went to NYC"
    """
    try:
        return template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing variable in prompt template: {e}")


def build_full_prompt(
    system_prompt: str,
    user_input: str,
    context: Dict[str, Any] = None
) -> str:
    """
    Build full prompt from system prompt and user input.

    Args:
        system_prompt: System instruction
        user_input: User's input text
        context: Optional context dictionary to include

    Returns:
        Complete prompt
    """
    parts = [system_prompt]

    if context:
        parts.append("\nContext:")
        for key, value in context.items():
            parts.append(f"- {key}: {value}")

    parts.append(f"\n\nUser Input: {user_input}")

    return "\n".join(parts)
