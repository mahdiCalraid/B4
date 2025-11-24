"""Base module interface for all processing modules."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class ModuleType(Enum):
    """Types of modules in the system."""
    INTERACTIVE = "interactive"  # User-facing, returns immediate response
    BACKGROUND = "background"    # Runs autonomously
    CONNECTOR = "connector"      # External API integration


class BaseModule(ABC):
    """
    Base interface all processing modules must implement.

    This ensures consistent behavior across all modules and enables
    the module registry to manage them uniformly.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.module_type = ModuleType.INTERACTIVE
        self.description = self.__doc__ or "No description provided"

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - must be implemented by all modules.

        Args:
            input_data: Dictionary containing request data with at minimum:
                - text: str (the main input text)
                - user_id: str (optional, identifier for the requester)

        Returns:
            Dictionary containing response data with at minimum:
                - response: str (the main output)
                - confidence: float (0-1, confidence in the result)
                - processing_time_ms: int (time taken to process)
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input before processing.

        Args:
            input_data: Input dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(input_data, dict):
            return False, "Input must be a dictionary"

        if "text" not in input_data:
            return False, "Input must contain 'text' field"

        return True, None

    def get_info(self) -> Dict[str, Any]:
        """
        Return module metadata.

        Returns:
            Dictionary with module information
        """
        return {
            "name": self.name,
            "version": self.version,
            "type": self.module_type.value,
            "description": self.description.strip().split('\n')[0]  # First line only
        }

    async def health_check(self) -> bool:
        """
        Check if module is healthy and ready to process requests.

        Returns:
            True if healthy, False otherwise
        """
        return True

    def _get_processing_metadata(self, start_time: datetime) -> Dict[str, Any]:
        """
        Helper to generate processing metadata.

        Args:
            start_time: When processing started

        Returns:
            Dictionary with processing metadata
        """
        processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return {
            "processing_time_ms": processing_time_ms,
            "module": self.name,
            "module_version": self.version,
            "timestamp": datetime.now().isoformat()
        }


# --- Tracing Infrastructure ---

class TraceEntry:
    """Represents a single step in an execution trace."""
    def __init__(
        self,
        trace_id: str,
        node_name: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.trace_id = trace_id
        self.node_name = node_name
        self.input_data = input_data
        self.output_data = output_data
        self.parent_id = parent_id
        self.timestamp = timestamp or datetime.now().isoformat()
        self.step_id = f"{node_name}_{datetime.now().timestamp()}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "step_id": self.step_id,
            "node_name": self.node_name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp
        }

# Global in-memory store for traces
# Structure: { trace_id: [TraceEntry, ...] }
TRACE_STORE: Dict[str, list] = {}

def add_trace_step(trace_id: str, node_name: str, input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None) -> None:
    """Record a step in the trace."""
    if trace_id not in TRACE_STORE:
        TRACE_STORE[trace_id] = []
    
    entry = TraceEntry(trace_id, node_name, input_data, output_data)
    TRACE_STORE[trace_id].append(entry)

def update_trace_step(trace_id: str, node_name: str, output_data: Dict[str, Any]) -> None:
    """Update the last step for this node with output data."""
    if trace_id in TRACE_STORE:
        # Find the last entry for this node that doesn't have output yet
        for entry in reversed(TRACE_STORE[trace_id]):
            if entry.node_name == node_name and entry.output_data is None:
                entry.output_data = output_data
                return
