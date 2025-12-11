# (1.) Custom exception classes
# (2.) Workflow engine specific errors

from typing import Any, Dict, Optional


class WorkflowEngineError(Exception):
    """
    (1.) Base exception for workflow engine errors
    (2.) All custom exceptions inherit from this
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        (1.) Initialize with message and optional details
        (2.) Details provide additional context for debugging
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class GraphNotFoundError(WorkflowEngineError):
    """
    (1.) Raised when graph_id does not exist
    (2.) HTTP 404 response
    """

    def __init__(self, graph_id: str):
        """
        (1.) Initialize with missing graph ID
        (2.) Provides clear error message
        """
        super().__init__(
            message=f"Graph not found: {graph_id}",
            details={"graph_id": graph_id}
        )


class RunNotFoundError(WorkflowEngineError):
    """
    (1.) Raised when run_id does not exist
    (2.) HTTP 404 response
    """

    def __init__(self, run_id: str):
        """
        (1.) Initialize with missing run ID
        (2.) Provides clear error message
        """
        super().__init__(
            message=f"Run not found: {run_id}",
            details={"run_id": run_id}
        )


class ValidationError(WorkflowEngineError):
    """
    (1.) Raised when graph configuration is invalid
    (2.) HTTP 400 response
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        (1.) Initialize with validation error details
        (2.) Details contain specific validation failures
        """
        super().__init__(message=message, details=details)


class ToolNotFoundError(WorkflowEngineError):
    """
    (1.) Raised when requested tool is not registered
    (2.) HTTP 400 response
    """

    def __init__(self, tool_name: str):
        """
        (1.) Initialize with missing tool name
        (2.) Provides clear error message
        """
        super().__init__(
            message=f"Tool not found: {tool_name}",
            details={"tool_name": tool_name}
        )


class LoopLimitError(WorkflowEngineError):
    """
    (1.) Raised when loop exceeds maximum iterations
    (2.) HTTP 500 response - indicates potential infinite loop
    """

    def __init__(self, node_name: str, max_iterations: int):
        """
        (1.) Initialize with loop details
        (2.) Helps identify problematic loop
        """
        super().__init__(
            message=f"Loop limit exceeded at node '{node_name}': max {max_iterations} iterations",
            details={"node": node_name, "max_iterations": max_iterations}
        )


class NodeExecutionError(WorkflowEngineError):
    """
    (1.) Raised when node execution fails
    (2.) HTTP 500 response
    """

    def __init__(self, node_name: str, original_error: Exception):
        """
        (1.) Initialize with node name and original exception
        (2.) Preserves original error for debugging
        """
        super().__init__(
            message=f"Node execution failed at '{node_name}': {str(original_error)}",
            details={"node": node_name, "original_error": str(original_error)}
        )


class SerializationError(WorkflowEngineError):
    """
    (1.) Raised when state cannot be serialized
    (2.) HTTP 400 response
    """

    def __init__(self, message: str):
        """
        (1.) Initialize with serialization error message
        (2.) Indicates non-JSON-serializable state
        """
        super().__init__(message=message)
