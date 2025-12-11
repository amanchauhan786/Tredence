# (1.) Graph Manager implementation
# (2.) Handles graph creation, validation, and retrieval

import uuid
from typing import List, Set

from app.engine.exceptions import GraphNotFoundError, ValidationError
from app.models.graph import GraphConfig
from app.storage.backend import StorageBackend


class GraphManager:
    """
    (1.) Manages workflow graph definitions
    (2.) Handles creation, validation, and storage
    """

    def __init__(self, storage: StorageBackend):
        """
        (1.) Initialize with storage backend
        (2.) Storage handles graph persistence
        """
        self._storage = storage

    def create_graph(self, config: GraphConfig) -> str:
        """
        (1.) Creates a new graph from configuration
        (2.) Returns unique graph_id
        """
        # (1.) Validate graph configuration
        # (2.) Raises ValidationError if invalid
        self._validate_graph(config)

        # (1.) Generate unique graph ID
        # (2.) UUID4 ensures uniqueness
        graph_id = str(uuid.uuid4())

        # (1.) Persist graph to storage
        # (2.) Graph can be retrieved later for execution
        self._storage.save_graph(graph_id, config)

        return graph_id

    def get_graph(self, graph_id: str) -> GraphConfig:
        """
        (1.) Retrieves graph by ID
        (2.) Raises GraphNotFoundError if not found
        """
        return self._storage.load_graph(graph_id)

    def has_graph(self, graph_id: str) -> bool:
        """
        (1.) Checks if graph exists
        (2.) Returns boolean without raising exception
        """
        return self._storage.has_graph(graph_id)

    def _validate_graph(self, config: GraphConfig) -> None:
        """
        (1.) Validates graph configuration
        (2.) Checks node references and entry point
        """
        errors: List[str] = []

        # (1.) Collect all node names
        # (2.) Used for edge validation
        node_names: Set[str] = {node.name for node in config.nodes}

        # (1.) Validate entry node exists
        # (2.) Entry point must be a defined node
        if config.entry_node not in node_names:
            errors.append(f"Entry node '{config.entry_node}' not found in nodes")

        # (1.) Validate edge references
        # (2.) Both source and target must exist
        for edge in config.edges:
            if edge.source not in node_names:
                errors.append(f"Edge source '{edge.source}' not found in nodes")
            if edge.target not in node_names:
                errors.append(f"Edge target '{edge.target}' not found in nodes")

        # (1.) Validate loop references
        # (2.) Loop nodes must exist
        if config.loops:
            for loop_node in config.loops.keys():
                if loop_node not in node_names:
                    errors.append(f"Loop node '{loop_node}' not found in nodes")

        # (1.) Raise validation error if any issues found
        # (2.) Include all errors in details
        if errors:
            raise ValidationError(
                message="Graph validation failed",
                details={"errors": errors}
            )
