"""Structure output handling utilities."""

import json
from pathlib import Path
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, create_model, Field


def load_schema(schema_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load JSON schema from file.

    Args:
        schema_path: Path to structure_output.json

    Returns:
        Schema dictionary or None if file doesn't exist
    """
    if not schema_path.exists():
        return None

    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_structure(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate data against JSON schema.

    Args:
        data: Data to validate
        schema: JSON schema

    Returns:
        True if valid, False otherwise
    """
    try:
        model = create_response_model(schema)
        model(**data)
        return True
    except Exception:
        return False


def create_response_model(
    schema: Dict[str, Any],
    model_name: str = "DynamicResponse"
) -> Type[BaseModel]:
    """
    Create Pydantic model from JSON schema.

    Args:
        schema: JSON schema with properties and types
        model_name: Name for the generated model

    Returns:
        Pydantic model class
    """
    properties = schema.get('properties', {})
    required = schema.get('required', [])

    # Build field definitions
    fields = {}

    for field_name, field_schema in properties.items():
        field_type = _json_type_to_python(field_schema)
        field_description = field_schema.get('description', '')
        is_required = field_name in required

        if is_required:
            fields[field_name] = (
                field_type,
                Field(..., description=field_description)
            )
        else:
            fields[field_name] = (
                Optional[field_type],
                Field(None, description=field_description)
            )

    return create_model(model_name, **fields)


def _json_type_to_python(field_schema: Dict[str, Any]) -> Type:
    """
    Convert JSON schema type to Python type.

    Args:
        field_schema: Field schema with type information

    Returns:
        Python type
    """
    json_type = field_schema.get('type', 'string')

    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list,
        'object': dict,
        'null': type(None)
    }

    python_type = type_mapping.get(json_type, str)

    # Handle array items
    if json_type == 'array' and 'items' in field_schema:
        item_type = _json_type_to_python(field_schema['items'])
        from typing import List
        return List[item_type]

    # Handle object properties
    if json_type == 'object' and 'properties' in field_schema:
        # Create nested model
        nested_schema = {
            'properties': field_schema['properties'],
            'required': field_schema.get('required', [])
        }
        return create_response_model(nested_schema, model_name="NestedObject")

    return python_type


def schema_to_json_string(schema: Dict[str, Any]) -> str:
    """
    Convert schema to formatted JSON string.

    Args:
        schema: JSON schema

    Returns:
        Formatted JSON string
    """
    return json.dumps(schema, indent=2)
