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
