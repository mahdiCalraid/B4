"""Base agent class for file-based agent definitions."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pathlib import Path
from pydantic import BaseModel
import json


class BaseAgent(ABC):
    """
    Base class for all file-based agents.

    Each agent is defined by a folder containing:
    - info.txt: Human-readable metadata
    - prompt.txt: System prompt for the agent
    - structure_output.json: JSON schema for output validation
    - config.py (optional): Python configuration
    - special_tools.py (optional): Agent-specific tools
    """

    def __init__(
        self,
        agent_id: str,
        agent_path: Path,
        ai_provider: Optional[Any] = None
    ):
        """
        Initialize base agent.

        Args:
            agent_id: Unique identifier for the agent
            agent_path: Path to agent definition folder
            ai_provider: AI provider instance (GeminiAgent, OpenAIAgent, etc.)
        """
        self.agent_id = agent_id
        self.agent_path = agent_path
        self.ai_provider = ai_provider

        # Load agent configuration
        self.info = self._load_info()
        self.prompt_template = self._load_prompt()
        self.output_schema = self._load_output_schema()
        self.config = self._load_config()

    def _load_info(self) -> Dict[str, str]:
        """Load info.txt file."""
        info_path = self.agent_path / "info.txt"
        if not info_path.exists():
            return {
                "name": self.agent_id,
                "description": "No description available",
                "role": "Generic agent",
                "input": "Text input",
                "output": "JSON output"
            }

        info = {}
        with open(info_path, 'r') as f:
            current_key = None
            current_value = []

            for line in f:
                line = line.rstrip()
                if line and ':' in line and not line.startswith(' '):
                    # New key
                    if current_key:
                        info[current_key] = '\n'.join(current_value).strip()

                    key, value = line.split(':', 1)
                    current_key = key.strip().lower()
                    current_value = [value.strip()] if value.strip() else []
                elif line and current_key:
                    # Continuation of previous value
                    current_value.append(line.strip())

            # Don't forget the last key
            if current_key:
                info[current_key] = '\n'.join(current_value).strip()

        return info

    def _load_prompt(self) -> str:
        """Load prompt.txt file."""
        prompt_path = self.agent_path / "prompt.txt"
        if not prompt_path.exists():
            return "You are a helpful AI assistant."

        with open(prompt_path, 'r') as f:
            return f.read().strip()

    def _load_output_schema(self) -> Optional[Dict[str, Any]]:
        """Load structure_output.json file."""
        schema_path = self.agent_path / "structure_output.json"
        if not schema_path.exists():
            return None

        with open(schema_path, 'r') as f:
            return json.load(f)

    def _load_config(self) -> Dict[str, Any]:
        """Load config.py file if it exists."""
        config_path = self.agent_path / "config.py"
        if not config_path.exists():
            return {}

        # Dynamic import of config
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        # Extract config dictionary or attributes
        if hasattr(config_module, 'config'):
            return config_module.config
        else:
            # Get all uppercase attributes as config
            return {
                k: v for k, v in vars(config_module).items()
                if k.isupper() and not k.startswith('_')
            }

    def _create_pydantic_model(self) -> Optional[Type[BaseModel]]:
        """Create a Pydantic model from the JSON schema."""
        if not self.output_schema:
            return None

        from pydantic import create_model

        # Extract properties from schema
        properties = self.output_schema.get('properties', {})
        required = self.output_schema.get('required', [])

        # Build field definitions
        fields = {}
        for field_name, field_schema in properties.items():
            field_type = self._json_type_to_python(field_schema)
            is_required = field_name in required

            if is_required:
                fields[field_name] = (field_type, ...)
            else:
                fields[field_name] = (Optional[field_type], None)

        # Create dynamic model
        model_name = f"{self.agent_id.title().replace('_', '')}Response"
        return create_model(model_name, **fields)

    def _json_type_to_python(self, field_schema: Dict[str, Any]) -> Type:
        """Convert JSON schema type to Python type."""
        json_type = field_schema.get('type', 'string')

        type_mapping = {
            'string': str,
            'integer': int,
            'number': float,
            'boolean': bool,
            'array': list,
            'object': dict
        }

        python_type = type_mapping.get(json_type, str)

        # Handle array items
        if json_type == 'array' and 'items' in field_schema:
            item_type = self._json_type_to_python(field_schema['items'])
            from typing import List
            return List[item_type]

        return python_type

    async def process(
        self,
        input_data: str,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process input through the agent with integrated logging.

        Args:
            input_data: Input text/message for the agent
            model: Optional model override (e.g., "gpt-4o", "gemini-2.0-flash")
            **kwargs: Additional parameters

        Returns:
            Processed result as dictionary
        """
        # Get the waterfall logger
        from agents.general_codes.waterfall_logger import get_waterfall_logger
        logger = get_waterfall_logger()

        # Log agent start
        logger.agent_start(self.agent_id, model)
        logger.agent_step(self.agent_id, "Received input", {
            "input_length": len(input_data),
            "model_requested": model
        })

        try:
            # Import here to avoid circular dependency
            from agents.general_codes.ai_model_selector import get_model_selector

            # Format the prompt with input_data
            # Some prompts have placeholders, some don't
            formatted_prompt = self.prompt_template
            if "{input_data}" in formatted_prompt:
                formatted_prompt = formatted_prompt.format(input_data=input_data)
            elif "{input}" in formatted_prompt:
                formatted_prompt = formatted_prompt.format(input=input_data)
            # If no placeholder, the input will be passed separately to the AI

            # If model is specified, use model selector instead of default provider
            if model:
                logger.agent_step(self.agent_id, "Using model selector", {"model": model})
                selector = get_model_selector()

                if self.output_schema:
                    logger.agent_step(self.agent_id, "Generating structured output")
                    response_model = self._create_pydantic_model()
                    result = await selector.generate_structured(
                        input_text=input_data,
                        output_schema=response_model,
                        model=model,
                        system_prompt=formatted_prompt,
                        **kwargs
                    )
                    final_result = result.model_dump() if hasattr(result, 'model_dump') else result
                else:
                    logger.agent_step(self.agent_id, "Generating unstructured output")
                    result = await selector.generate(
                        input_text=input_data,
                        model=model,
                        system_prompt=formatted_prompt,
                        **kwargs
                    )
                    final_result = {"result": result}

                logger.agent_step(self.agent_id, "AI processing complete", {
                    "output_keys": list(final_result.keys()) if isinstance(final_result, dict) else "non-dict"
                })
                logger.agent_result(self.agent_id, final_result)
                return final_result

            # Use default provider
            if not self.ai_provider:
                error_msg = f"Agent {self.agent_id} has no AI provider configured"
                logger.agent_error(self.agent_id, error_msg)
                raise ValueError(error_msg)

            logger.agent_step(self.agent_id, "Using default provider")

            # Use structured output if schema is defined
            if self.output_schema:
                logger.agent_step(self.agent_id, "Generating structured output with default provider")
                response_model = self._create_pydantic_model()
                result = await self.ai_provider.generate_structured(
                    prompt=input_data,
                    response_model=response_model,
                    system_prompt=formatted_prompt,
                    **kwargs
                )
                final_result = result.model_dump() if hasattr(result, 'model_dump') else result
            else:
                # Fallback to plain text generation
                logger.agent_step(self.agent_id, "Generating unstructured output with default provider")
                result = await self.ai_provider.generate(
                    prompt=input_data,
                    system_prompt=formatted_prompt,
                    **kwargs
                )
                final_result = {"result": result}

            logger.agent_result(self.agent_id, final_result)
            return final_result

        except Exception as e:
            logger.agent_error(self.agent_id, str(e), e)
            raise

    def get_info(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "agent_id": self.agent_id,
            "name": self.info.get("name", self.agent_id),
            "description": self.info.get("description", ""),
            "role": self.info.get("role", ""),
            "input": self.info.get("input", ""),
            "output": self.info.get("output", ""),
            "has_schema": self.output_schema is not None,
            "config": self.config,
            "provider": self.ai_provider.get_info() if self.ai_provider else None
        }
