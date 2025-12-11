# (1.) API request and response models
# (2.) Pydantic models for FastAPI endpoints

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.models.execution import ExecutionLog
from app.models.graph import GraphConfig


class CreateGraphRequest(BaseModel):
    """
    (1.) Request body for graph creation
    (2.) Contains full graph configuration
    """
    config: GraphConfig = Field(..., description="Graph configuration")


class CreateGraphResponse(BaseModel):
    """
    (1.) Response for successful graph creation
    (2.) Returns generated graph ID
    """
    graph_id: str = Field(..., description="Unique graph identifier")


class RunGraphRequest(BaseModel):
    """
    (1.) Request body for graph execution
    (2.) Contains graph ID and initial state
    """
    graph_id: str = Field(..., description="ID of graph to execute")
    initial_state: Dict[str, Any] = Field(default_factory=dict, description="Initial workflow state")


class RunGraphResponse(BaseModel):
    """
    (1.) Response for completed execution
    (2.) Contains final state and execution logs
    """
    run_id: str = Field(..., description="Unique run identifier")
    status: str = Field(..., description="Execution status")
    final_state: Dict[str, Any] = Field(..., description="Final workflow state")
    execution_log: List[ExecutionLog] = Field(..., description="Ordered execution log")


class StateResponse(BaseModel):
    """
    (1.) Response for state query
    (2.) Returns current run state
    """
    run_id: str = Field(..., description="Run identifier")
    status: str = Field(..., description="Current run status")
    current_state: Dict[str, Any] = Field(..., description="Current workflow state")


class ErrorResponse(BaseModel):
    """
    (1.) Standard error response format
    (2.) Includes error type and message
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
