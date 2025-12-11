# (1.) State Manager implementation
# (2.) Manages workflow state across execution

from datetime import datetime
from typing import Any, Dict

from app.engine.exceptions import RunNotFoundError
from app.models.execution import RunData
from app.storage.backend import StorageBackend


class StateManager:
    """
    (1.) Manages workflow state during execution
    (2.) Provides thread-safe state access via storage backend
    """

    def __init__(self, storage: StorageBackend):
        """
        (1.) Initialize with storage backend
        (2.) Storage handles persistence of run data
        """
        self._storage = storage

    def initialize(self, run_id: str, graph_id: str, initial_state: Dict[str, Any]) -> RunData:
        """
        (1.) Initializes state for new run
        (2.) Creates and stores initial RunData
        """
        run_data = RunData(
            run_id=run_id,
            graph_id=graph_id,
            current_state=initial_state.copy(),
            status="running",
            started_at=datetime.utcnow(),
            execution_log=[]
        )
        self._storage.save_run(run_id, run_data)
        return run_data

    def get_state(self, run_id: str) -> Dict[str, Any]:
        """
        (1.) Retrieves current state for run
        (2.) Raises RunNotFoundError if not found
        """
        run_data = self._storage.load_run(run_id)
        return run_data.current_state.copy()

    def get_run(self, run_id: str) -> RunData:
        """
        (1.) Retrieves full run data
        (2.) Raises RunNotFoundError if not found
        """
        return self._storage.load_run(run_id)

    def update_state(self, run_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        (1.) Merges updates into current state
        (2.) Returns new state after merge
        """
        run_data = self._storage.load_run(run_id)
        run_data.current_state.update(updates)
        self._storage.save_run(run_id, run_data)
        return run_data.current_state.copy()

    def set_state(self, run_id: str, state: Dict[str, Any]) -> None:
        """
        (1.) Replaces current state entirely
        (2.) Used when node returns complete state
        """
        run_data = self._storage.load_run(run_id)
        run_data.current_state = state.copy()
        self._storage.save_run(run_id, run_data)

    def update_run(self, run_data: RunData) -> None:
        """
        (1.) Saves updated run data
        (2.) Used for status and log updates
        """
        self._storage.save_run(run_data.run_id, run_data)

    def complete_run(self, run_id: str, status: str = "completed") -> RunData:
        """
        (1.) Marks run as completed
        (2.) Sets completion timestamp
        """
        run_data = self._storage.load_run(run_id)
        run_data.status = status
        run_data.completed_at = datetime.utcnow()
        self._storage.save_run(run_id, run_data)
        return run_data
