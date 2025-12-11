# (1.) Graph configuration models
# (2.) Pydantic models for defining workflow graphs

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ConditionConfig(BaseModel):
    """
    (1.) Condition for branching decisions
    (2.) Evaluates state field against value using operator
    """
    field: str = Field(..., description="State field to evaluate")
    operator: str = Field(..., description="Comparison operator: eq, ne, gt, lt, gte, lte")
    value: Any = Field(..., description="Value to compare against")

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        """
        (1.) Validates operator is supported
        (2.) Raises ValueError for invalid operators
        """
        valid_ops = {"eq", "ne", "gt", "lt", "gte", "lte"}
        if v not in valid_ops:
            raise ValueError(f"Operator must be one of: {valid_ops}")
        return v


class LoopConfig(BaseModel):
    """
    (1.) Loop configuration for repeated execution
    (2.) Includes max iterations safety limit
    """
    condition: ConditionConfig = Field(..., description="Condition to continue looping")
    max_iterations: int = Field(default=100, ge=1, description="Maximum loop iterations")


class NodeConfig(BaseModel):
    """
    (1.) Configuration for a single workflow node
    (2.) References a handler function by name
    """
    name: str = Field(..., description="Unique node identifier")
    handler: str = Field(..., description="Name of handler function in tool registry")
    description: Optional[str] = Field(default=None, description="Human-readable description")


class EdgeConfig(BaseModel):
    """
    (1.) Defines connection between nodes
    (2.) Optional condition for branching
    """
    source: str = Field(..., description="Source node name")
    target: str = Field(..., description="Target node name")
    condition: Optional[ConditionConfig] = Field(default=None, description="Optional branching condition")


class GraphConfig(BaseModel):
    """
    (1.) Complete graph definition
    (2.) Contains nodes, edges, entry point, and optional loops
    """
    name: str = Field(..., description="Graph name")
    nodes: List[NodeConfig] = Field(..., min_length=1, description="List of workflow nodes")
    edges: List[EdgeConfig] = Field(default_factory=list, description="List of node connections")
    entry_node: str = Field(..., description="Name of the starting node")
    loops: Optional[Dict[str, LoopConfig]] = Field(default=None, description="Loop configurations by node name")

    @field_validator("nodes")
    @classmethod
    def validate_unique_node_names(cls, v: List[NodeConfig]) -> List[NodeConfig]:
        """
        (1.) Ensures all node names are unique
        (2.) Raises ValueError for duplicate names
        """
        names = [node.name for node in v]
        if len(names) != len(set(names)):
            raise ValueError("Node names must be unique")
        return v
