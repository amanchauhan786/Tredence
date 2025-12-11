# (1.) Workflow Executor implementation
# (2.) Executes graphs by traversing nodes according to edges

import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from app.engine.exceptions import (
    LoopLimitError,
    NodeExecutionError,
    ToolNotFoundError,
)
from app.engine.graph_manager import GraphManager
from app.engine.state_manager import StateManager
from app.models.execution import ExecutionLog, ExecutionResult
from app.models.graph import ConditionConfig, GraphConfig
from app.tools.registry import ToolRegistry


class WorkflowExecutor:
    """
    (1.) Executes workflow graphs
    (2.) Handles node execution, branching, and looping
    """

    def __init__(
        self,
        graph_manager: GraphManager,
        state_manager: StateManager,
        tool_registry: ToolRegistry
    ):
        """
        (1.) Initialize with required managers
        (2.) Dependencies injected for testability
        """
        self._graph_manager = graph_manager
        self._state_manager = state_manager
        self._tool_registry = tool_registry

    def execute(self, graph_id: str, initial_state: Dict[str, Any]) -> ExecutionResult:
        """
        (1.) Executes workflow from start to completion
        (2.) Returns final state and execution log
        """
        # (1.) Generate unique run ID
        # (2.) Used for state tracking
        run_id = str(uuid.uuid4())

        # (1.) Load graph configuration
        # (2.) Raises GraphNotFoundError if not found
        graph = self._graph_manager.get_graph(graph_id)

        # (1.) Initialize run state
        # (2.) Creates RunData in storage
        self._state_manager.initialize(run_id, graph_id, initial_state)

        execution_log: List[ExecutionLog] = []
        current_node = graph.entry_node
        loop_counts: Dict[str, int] = {}

        try:
            # (1.) Execute nodes until workflow completes
            # (2.) None indicates no more nodes to execute
            while current_node is not None:
                # (1.) Execute current node
                # (2.) Returns log entry for this execution
                log_entry = self._execute_node(run_id, current_node, graph)
                execution_log.append(log_entry)

                # (1.) Check for loop at current node
                # (2.) Handle loop iteration or exit
                if graph.loops and current_node in graph.loops:
                    loop_config = graph.loops[current_node]
                    loop_counts[current_node] = loop_counts.get(current_node, 0) + 1

                    # (1.) Check loop iteration limit
                    # (2.) Prevent infinite loops
                    if loop_counts[current_node] > loop_config.max_iterations:
                        raise LoopLimitError(current_node, loop_config.max_iterations)

                    # (1.) Evaluate loop condition
                    # (2.) Continue loop if condition is true
                    current_state = self._state_manager.get_state(run_id)
                    if self._evaluate_condition(loop_config.condition, current_state):
                        # (1.) Stay on current node for next iteration
                        # (2.) Loop continues
                        continue

                # (1.) Determine next node
                # (2.) Based on edges and conditions
                current_node = self._get_next_node(current_node, run_id, graph)

            # (1.) Mark run as completed
            # (2.) Update status and timestamp
            run_data = self._state_manager.complete_run(run_id, "completed")

            return ExecutionResult(
                run_id=run_id,
                graph_id=graph_id,
                status="completed",
                final_state=run_data.current_state,
                execution_log=execution_log
            )

        except Exception as e:
            # (1.) Mark run as failed
            # (2.) Preserve error information
            self._state_manager.complete_run(run_id, "failed")

            return ExecutionResult(
                run_id=run_id,
                graph_id=graph_id,
                status="failed",
                final_state=self._state_manager.get_state(run_id),
                execution_log=execution_log,
                error=str(e)
            )

    def _execute_node(
        self,
        run_id: str,
        node_name: str,
        graph: GraphConfig
    ) -> ExecutionLog:
        """
        (1.) Executes single node with current state
        (2.) Returns execution log entry
        """
        # (1.) Find node configuration
        # (2.) Get handler name
        node_config = next(n for n in graph.nodes if n.name == node_name)

        # (1.) Get handler function from registry
        # (2.) Raises ToolNotFoundError if not registered
        handler = self._tool_registry.get(node_config.handler)

        # (1.) Get current state before execution
        # (2.) Used for logging
        state_before = self._state_manager.get_state(run_id)

        # (1.) Execute handler with state
        # (2.) Measure execution time
        start_time = time.time()
        try:
            result = handler(state_before.copy())
            status = "success"
        except Exception as e:
            raise NodeExecutionError(node_name, e)

        duration_ms = (time.time() - start_time) * 1000

        # (1.) Update state with result
        # (2.) Merge returned dictionary into state
        if isinstance(result, dict):
            self._state_manager.update_state(run_id, result)

        # (1.) Get state after execution
        # (2.) Used for logging
        state_after = self._state_manager.get_state(run_id)

        return ExecutionLog(
            node=node_name,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
            state_before=state_before,
            state_after=state_after,
            status=status
        )

    def _evaluate_condition(
        self,
        condition: ConditionConfig,
        state: Dict[str, Any]
    ) -> bool:
        """
        (1.) Evaluates branching/loop condition
        (2.) Returns boolean result
        """
        # (1.) Get field value from state
        # (2.) Default to None if not present
        field_value = state.get(condition.field)

        # (1.) Compare using specified operator
        # (2.) Supported: eq, ne, gt, lt, gte, lte
        operators = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
        }

        op_func = operators.get(condition.operator)
        if op_func is None:
            return False

        try:
            return op_func(field_value, condition.value)
        except TypeError:
            # (1.) Handle incompatible types
            # (2.) Return False for comparison failures
            return False

    def _get_next_node(
        self,
        current: str,
        run_id: str,
        graph: GraphConfig
    ) -> Optional[str]:
        """
        (1.) Determines next node based on edges and conditions
        (2.) Returns None if workflow should terminate
        """
        current_state = self._state_manager.get_state(run_id)

        # (1.) Find edges from current node
        # (2.) Check conditions in order
        for edge in graph.edges:
            if edge.source != current:
                continue

            # (1.) Check edge condition if present
            # (2.) Skip edge if condition is false
            if edge.condition is not None:
                if not self._evaluate_condition(edge.condition, current_state):
                    continue

            # (1.) Return target of first matching edge
            # (2.) Conditions evaluated in definition order
            return edge.target

        # (1.) No matching edge found
        # (2.) Workflow terminates
        return None
