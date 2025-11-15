"""
General utility codes for agents.

This module provides shared functionality for all agents including:
- AI API calling
- AI model selection and management
- Prompt reading and formatting
- Structure output handling
- Results processing
- Tool calling
"""

from .ai_api_call import call_ai_api, call_ai_structured
from .ai_model_selector import get_model_selector, list_available_models, get_model_info
from .prompt_reader import read_prompt, format_prompt
from .structure_handler import validate_structure, create_response_model
from .result_handler import process_result, format_response

__all__ = [
    "call_ai_api",
    "call_ai_structured",
    "get_model_selector",
    "list_available_models",
    "get_model_info",
    "read_prompt",
    "format_prompt",
    "validate_structure",
    "create_response_model",
    "process_result",
    "format_response"
]
