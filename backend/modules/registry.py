"""Module registry for managing all processing modules."""

from typing import Dict, Type, Optional, List
from .base import BaseModule, ModuleType


class ModuleRegistry:
    """
    Central registry for all processing modules.

    Manages module registration, discovery, and retrieval.
    """

    def __init__(self):
        self._modules: Dict[str, Type[BaseModule]] = {}
        self._instances: Dict[str, BaseModule] = {}

    def register(self, module_class: Type[BaseModule]) -> None:
        """
        Register a module class.

        Args:
            module_class: The module class to register
        """
        module_name = module_class.__name__
        self._modules[module_name] = module_class
        print(f"✅ Registered module: {module_name}")

    def get_module(self, module_name: str) -> BaseModule:
        """
        Get a module instance by name.

        Creates a new instance if one doesn't exist yet.

        Args:
            module_name: Name of the module to retrieve

        Returns:
            Module instance

        Raises:
            ValueError: If module not found
        """
        if module_name not in self._modules:
            available = ", ".join(self._modules.keys())
            raise ValueError(
                f"Module '{module_name}' not found. "
                f"Available modules: {available}"
            )

        # Return cached instance or create new one
        if module_name not in self._instances:
            self._instances[module_name] = self._modules[module_name]()

        return self._instances[module_name]

    def list_modules(
        self,
        module_type: Optional[ModuleType] = None
    ) -> Dict[str, Dict]:
        """
        List all registered modules.

        Args:
            module_type: Optional filter by module type

        Returns:
            Dictionary of module names to their info
        """
        modules = {}

        for name, module_class in self._modules.items():
            instance = self.get_module(name)

            if module_type is None or instance.module_type == module_type:
                modules[name] = instance.get_info()

        return modules

    def module_exists(self, module_name: str) -> bool:
        """
        Check if a module is registered.

        Args:
            module_name: Name to check

        Returns:
            True if module exists
        """
        return module_name in self._modules

    def get_module_count(self) -> int:
        """
        Get total number of registered modules.

        Returns:
            Count of modules
        """
        return len(self._modules)


# Global registry instance
registry = ModuleRegistry()
