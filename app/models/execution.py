# (1.) Execution models
# (2.) Pydantic models for workflow execution state and results

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionLog(BaseModel):
    """
    (1.) Log entry for single node execution
    (2.) Captures timing and state changes
    """
    node: str = Field(..., description="Name of executed node")
    timestamp: datetime = Field(..., description="Execution start time")
    duration_ms: float = Field(..., ge=0, description="Execution duration in milliseconds")
    state_before: Dict[str, Any] = Field(..., description="State before node execution")
    state_after: Dict[str, Any] = Field(..., description="State after node execution")
    status: str = Field(..., description="Execution status: success or error")


class ExecutionResult(BaseModel):
    """
    (1.) Complete result of workflow execution
    (2.) Contains final state and full execution log
    """
    run_id: str = Field(..., description="Unique run identifier")
    graph_id: str = Field(..., description="ID of executed graph")
    status: str = Field(..., description="Workflow status: completed, failed, running")
    final_state: Dict[str, Any] = Field(..., description="Final state after execution")
    execution_log: List[ExecutionLog] = Field(default_factory=list, description="Ordered execution log")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class RunData(BaseModel):
    """
    (1.) Persistent data for a workflow run
    (2.) Used for state queries during execution
    """
    run_id: str = Field(..., description="Unique run identifier")
    graph_id: str = Field(..., description="ID of the graph being executed")
    current_state: Dict[str, Any] = Field(..., description="Current workflow state")
    status: str = Field(..., description="Run status: running, completed, failed")
    started_at: datetime = Field(..., description="Run start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Run completion timestamp")
    execution_log: List[ExecutionLog] = Field(default_factory=list, description="Execution log entries")
