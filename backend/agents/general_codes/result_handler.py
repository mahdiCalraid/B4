"""Result processing and formatting utilities."""

from typing import Dict, Any, Optional
from pydantic import BaseModel
import json


def process_result(
    result: Any,
    expected_type: str = "json"
) -> Dict[str, Any]:
    """
    Process agent result into standard format.

    Args:
        result: Raw result from agent (could be string, dict, or Pydantic model)
        expected_type: Expected result type (json, text, structured)

    Returns:
        Processed result as dictionary
    """
    # Handle Pydantic models
    if isinstance(result, BaseModel):
        return {
            "success": True,
            "data": result.model_dump(),
            "type": "structured"
        }

    # Handle dictionaries
    if isinstance(result, dict):
        return {
            "success": True,
            "data": result,
            "type": "json"
        }

    # Handle strings
    if isinstance(result, str):
        # Try to parse as JSON
        if expected_type == "json":
            try:
                parsed = json.loads(result)
                return {
                    "success": True,
                    "data": parsed,
                    "type": "json"
                }
            except json.JSONDecodeError:
                pass

        return {
            "success": True,
            "data": {"text": result},
            "type": "text"
        }

    # Fallback
    return {
        "success": True,
        "data": {"result": str(result)},
        "type": "unknown"
    }


def format_response(
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format response with metadata.

    Args:
        data: Response data
        metadata: Optional metadata to include

    Returns:
        Formatted response
    """
    response = {
        "success": True,
        "data": data
    }

    if metadata:
        response["metadata"] = metadata

    return response


def extract_from_result(
    result: Dict[str, Any],
    field_path: str,
    default: Any = None
) -> Any:
    """
    Extract field from nested result using dot notation.

    Args:
        result: Result dictionary
        field_path: Dot-separated path (e.g., "data.people.0.name")
        default: Default value if field not found

    Returns:
        Extracted value or default
    """
    parts = field_path.split('.')
    current = result

    for part in parts:
        if isinstance(current, dict):
            current = current.get(part, default)
        elif isinstance(current, list):
            try:
                index = int(part)
                current = current[index]
            except (ValueError, IndexError):
                return default
        else:
            return default

        if current is None:
            return default

    return current


def merge_results(
    *results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge multiple agent results into one.

    Args:
        *results: Multiple result dictionaries

    Returns:
        Merged result
    """
    merged = {
        "success": True,
        "data": {},
        "sources": []
    }

    for idx, result in enumerate(results):
        if isinstance(result, dict) and "data" in result:
            # Merge data
            if isinstance(result["data"], dict):
                merged["data"].update(result["data"])
            else:
                merged["data"][f"result_{idx}"] = result["data"]

            # Track sources
            merged["sources"].append({
                "index": idx,
                "type": result.get("type", "unknown")
            })

    return merged
