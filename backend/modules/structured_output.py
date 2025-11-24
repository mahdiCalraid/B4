"""Structured Output Node - Parses AI output into JSON schema."""

from typing import Dict, Any
import json
import re
from pydantic import BaseModel, Field, create_model


class StructuredOutputNode:
    """
    Node that enforces structured output from AI agents.
    Takes unstructured text and parses it according to a JSON schema.
    """
    
    def __init__(self):
        pass
    
    def get_schema(self):
        """Return node schema."""
        from schema.node import NodeSchema, NodeType, NodeConfig
        
        return NodeSchema(
            id="structured-output",
            name="Structured Output",
            category="logic",
            type=NodeType.LOGIC,
            description="Parses AI output into structured JSON format",
            icon="file-json",
            color="#8b5cf6",
            config_schema=[
                NodeConfig(
                    name="schema",
                    type="string",
                    label="JSON Schema",
                    description="JSON schema for output structure",
                    required=True
                ),
                NodeConfig(
                    name="strict",
                    type="boolean",
                    label="Strict Mode",
                    description="Fail if output doesn't match schema",
                    default=False
                )
            ],
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Raw AI output text"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "parsed": {"type": "object", "description": "Parsed structured output"},
                    "valid": {"type": "boolean", "description": "Whether output matches schema"}
                }
            }
        )
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text that might have markdown or other formatting."""
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find raw JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Try parsing the entire text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Simple schema validation."""
        if not schema:
            return True
        
        required = schema.get('required', [])
        properties = schema.get('properties', {})
        
        # Check required fields
        for field in required:
            if field not in data:
                return False
        
        # Check types
        for field, field_schema in properties.items():
            if field in data:
                expected_type = field_schema.get('type')
                actual_value = data[field]
                
                type_map = {
                    'string': str,
                    'integer': int,
                    'number': (int, float),
                    'boolean': bool,
                    'array': list,
                    'object': dict
                }
                
                if expected_type in type_map:
                    if not isinstance(actual_value, type_map[expected_type]):
                        return False
        
        return True
    
    async def process(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input through structured output parsing.
        
        Args:
            input_data: Must contain 'text' field with AI output
            config: Must contain 'schema' field with JSON schema
        
        Returns:
            Dict with 'parsed' and 'valid' fields
        """
        text = input_data.get('text', '')
        schema_str = config.get('schema', '{}')
        strict = config.get('strict', False)
        
        # Parse schema
        try:
            schema = json.loads(schema_str) if isinstance(schema_str, str) else schema_str
        except json.JSONDecodeError:
            schema = {}
        
        # Extract JSON from text
        parsed = self._extract_json_from_text(text)
        
        # Validate
        valid = self._validate_against_schema(parsed, schema)
        
        if strict and not valid:
            raise ValueError(f"Output does not match schema. Got: {parsed}")
        
        return {
            "parsed": parsed,
            "valid": valid,
            "raw_text": text
        }
