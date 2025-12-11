# (1.) Storage backend interface and implementations
# (2.) Abstract base class and in-memory storage

from abc import ABC, abstractmethod
from typing import Dict

from app.engine.exceptions import GraphNotFoundError, RunNotFoundError
from app.models.execution import RunData
from app.models.graph import GraphConfig


class StorageBackend(ABC):
    """
    (1.) Abstract interface for storage operations
    (2.) Defines contract for graph and run persistence
    """

    @abstractmethod
    def save_graph(self, graph_id: str, config: GraphConfig) -> None:
        """
        (1.) Persists graph configuration
        (2.) Overwrites if graph_id exists
        """
        pass

    @abstractmethod
    def load_graph(self, graph_id: str) -> GraphConfig:
        """
        (1.) Retrieves graph by ID
        (2.) Raises GraphNotFoundError if not found
        """
        pass

    @abstractmethod
    def has_graph(self, graph_id: str) -> bool:
        """
        (1.) Checks if graph exists
        (2.) Returns boolean without raising exception
        """
        pass

    @abstractmethod
    def save_run(self, run_id: str, run_data: RunData) -> None:
        """
        (1.) Persists run data
        (2.) Overwrites if run_id exists
        """
        pass

    @abstractmethod
    def load_run(self, run_id: str) -> RunData:
        """
        (1.) Retrieves run by ID
        (2.) Raises RunNotFoundError if not found
        """
        pass

    @abstractmethod
    def has_run(self, run_id: str) -> bool:
        """
        (1.) Checks if run exists
        (2.) Returns boolean without raising exception
        """
        pass


class InMemoryStorage(StorageBackend):
    """
    (1.) In-memory storage implementation
    (2.) Stores graphs and runs in dictionaries
    """

    def __init__(self):
        """
        (1.) Initialize empty storage
        (2.) Separate dictionaries for graphs and runs
        """
        self._graphs: Dict[str, GraphConfig] = {}
        self._runs: Dict[str, RunData] = {}

    def save_graph(self, graph_id: str, config: GraphConfig) -> None:
        """
        (1.) Stores graph in memory
        (2.) Overwrites existing graph with same ID
        """
        self._graphs[graph_id] = config

    def load_graph(self, graph_id: str) -> GraphConfig:
        """
        (1.) Retrieves graph from memory
        (2.) Raises GraphNotFoundError if not found
        """
        if graph_id not in self._graphs:
            raise GraphNotFoundError(graph_id)
        return self._graphs[graph_id]

    def has_graph(self, graph_id: str) -> bool:
        """
        (1.) Checks if graph exists in memory
        (2.) Returns boolean
        """
        return graph_id in self._graphs

    def save_run(self, run_id: str, run_data: RunData) -> None:
        """
        (1.) Stores run data in memory
        (2.) Overwrites existing run with same ID
        """
        self._runs[run_id] = run_data

    def load_run(self, run_id: str) -> RunData:
        """
        (1.) Retrieves run from memory
        (2.) Raises RunNotFoundError if not found
        """
        if run_id not in self._runs:
            raise RunNotFoundError(run_id)
        return self._runs[run_id]

    def has_run(self, run_id: str) -> bool:
        """
        (1.) Checks if run exists in memory
        (2.) Returns boolean
        """
        return run_id in self._runs

    def clear(self) -> None:
        """
        (1.) Clears all stored data
        (2.) Useful for testing
        """
        self._graphs.clear()
        self._runs.clear()
