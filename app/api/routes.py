# (1.) API route definitions
# (2.) FastAPI endpoints for graph operations

from fastapi import APIRouter, HTTPException

from app.engine import (
    GraphManager,
    GraphNotFoundError,
    RunNotFoundError,
    StateManager,
    ValidationError,
    WorkflowExecutor,
)
from app.models import (
    CreateGraphRequest,
    CreateGraphResponse,
    ErrorResponse,
    RunGraphRequest,
    RunGraphResponse,
    StateResponse,
)
from app.storage import InMemoryStorage
from app.tools import tool_registry

# (1.) Initialize shared storage backend
# (2.) Single instance for all components
storage = InMemoryStorage()

# (1.) Initialize managers with shared storage
# (2.) Dependency injection pattern
graph_manager = GraphManager(storage)
state_manager = StateManager(storage)
executor = WorkflowExecutor(graph_manager, state_manager, tool_registry)

# (1.) Create API router
# (2.) All routes prefixed with /graph in main.py
router = APIRouter()


@router.post(
    "/create",
    response_model=CreateGraphResponse,
    responses={400: {"model": ErrorResponse}}
)
async def create_graph(request: CreateGraphRequest) -> CreateGraphResponse:
    """
    (1.) Creates a new workflow graph
    (2.) Returns unique graph_id on success
    """
    try:
        graph_id = graph_manager.create_graph(request.config)
        return CreateGraphResponse(graph_id=graph_id)
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "ValidationError", "message": e.message, "details": e.details}
        )


@router.post(
    "/run",
    response_model=RunGraphResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def run_graph(request: RunGraphRequest) -> RunGraphResponse:
    """
    (1.) Executes a workflow graph
    (2.) Returns final state and execution log
    """
    try:
        result = executor.execute(request.graph_id, request.initial_state)

        if result.status == "failed":
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "ExecutionError",
                    "message": result.error or "Workflow execution failed",
                    "details": {"run_id": result.run_id}
                }
            )

        return RunGraphResponse(
            run_id=result.run_id,
            status=result.status,
            final_state=result.final_state,
            execution_log=result.execution_log
        )
    except GraphNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": "GraphNotFoundError", "message": e.message, "details": e.details}
        )


@router.get(
    "/state/{run_id}",
    response_model=StateResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_state(run_id: str) -> StateResponse:
    """
    (1.) Returns current state of a workflow run
    (2.) Used for monitoring execution progress
    """
    try:
        run_data = state_manager.get_run(run_id)
        return StateResponse(
            run_id=run_data.run_id,
            status=run_data.status,
            current_state=run_data.current_state
        )
    except RunNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": "RunNotFoundError", "message": e.message, "details": e.details}
        )
