# (1.) Tool Registry implementation
# (2.) Manages registration and retrieval of callable tools

from typing import Callable, Dict, List

from app.engine.exceptions import ToolNotFoundError


class ToolRegistry:
    """
    (1.) Registry for workflow tools
    (2.) Stores callable functions that nodes can invoke
    """

    def __init__(self):
        """
        (1.) Initialize empty tool registry
        (2.) Tools stored as name -> callable mapping
        """
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        """
        (1.) Registers tool function by name
        (2.) Overwrites if name already exists
        """
        self._tools[name] = func

    def get(self, name: str) -> Callable:
        """
        (1.) Retrieves tool by name
        (2.) Raises ToolNotFoundError if not found
        """
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    def list_tools(self) -> List[str]:
        """
        (1.) Returns list of registered tool names
        (2.) Used for discovery and validation
        """
        return list(self._tools.keys())

    def has(self, name: str) -> bool:
        """
        (1.) Checks if tool is registered
        (2.) Returns boolean without raising exception
        """
        return name in self._tools

    def clear(self) -> None:
        """
        (1.) Removes all registered tools
        (2.) Useful for testing and reset scenarios
        """
        self._tools.clear()


# (1.) Global tool registry instance
# (2.) Shared across the application
tool_registry = ToolRegistry()
