# (1.) Code Review workflow implementation
# (2.) Sample workflow demonstrating engine capabilities

import re
from typing import Any, Dict, List

from app.models.graph import (
    ConditionConfig,
    EdgeConfig,
    GraphConfig,
    LoopConfig,
    NodeConfig,
)
from app.tools import tool_registry


def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    (1.) Extracts function definitions from code
    (2.) Uses regex to find function names
    """
    code = state.get("code", "")

    # (1.) Find all function definitions
    # (2.) Supports def keyword for Python functions
    pattern = r"def\s+(\w+)\s*\("
    matches = re.findall(pattern, code)

    return {
        "functions": matches,
        "function_count": len(matches)
    }


def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    (1.) Calculates code complexity score
    (2.) Based on function count and code length
    """
    code = state.get("code", "")
    functions = state.get("functions", [])

    # (1.) Simple complexity heuristics
    # (2.) Lines of code and nesting depth
    lines = code.split("\n")
    line_count = len([l for l in lines if l.strip()])

    # (1.) Count control flow statements
    # (2.) Indicates branching complexity
    control_keywords = ["if", "for", "while", "try", "except"]
    control_count = sum(
        1 for line in lines
        for kw in control_keywords
        if re.search(rf"\b{kw}\b", line)
    )

    # (1.) Calculate complexity score
    # (2.) Lower is better, scale 0-100
    base_score = 100
    penalty = (line_count * 0.5) + (control_count * 2)
    complexity_score = max(0, base_score - penalty)

    return {
        "line_count": line_count,
        "control_count": control_count,
        "complexity_score": round(complexity_score, 2)
    }


def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    (1.) Detects basic code issues
    (2.) Rule-based pattern matching
    """
    code = state.get("code", "")
    issues: List[str] = []

    # (1.) Check for common issues
    # (2.) Simple pattern-based detection
    if "print(" in code:
        issues.append("Debug print statements found")

    if "TODO" in code or "FIXME" in code:
        issues.append("Unresolved TODO/FIXME comments")

    if "pass" in code:
        issues.append("Empty pass statements found")

    if "import *" in code:
        issues.append("Wildcard imports detected")

    # (1.) Check for long lines
    # (2.) PEP 8 recommends 79 characters
    for i, line in enumerate(code.split("\n"), 1):
        if len(line) > 100:
            issues.append(f"Line {i} exceeds 100 characters")
            break

    return {
        "issues": issues,
        "issue_count": len(issues)
    }


def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    (1.) Generates improvement suggestions
    (2.) Based on detected issues and complexity
    """
    issues = state.get("issues", [])
    complexity_score = state.get("complexity_score", 0)
    suggestions: List[str] = []

    # (1.) Generate suggestions based on issues
    # (2.) Actionable recommendations
    if "Debug print statements found" in issues:
        suggestions.append("Replace print statements with proper logging")

    if "Unresolved TODO/FIXME comments" in issues:
        suggestions.append("Address or remove TODO/FIXME comments")

    if "Empty pass statements found" in issues:
        suggestions.append("Implement or remove empty pass blocks")

    if "Wildcard imports detected" in issues:
        suggestions.append("Use explicit imports instead of wildcard")

    # (1.) Suggestions based on complexity
    # (2.) Refactoring recommendations
    if complexity_score < 50:
        suggestions.append("Consider breaking down complex functions")

    if state.get("function_count", 0) > 10:
        suggestions.append("Consider splitting into multiple modules")

    # (1.) Calculate quality score
    # (2.) Combines complexity and issue count
    issue_penalty = len(issues) * 10
    quality_score = max(0, complexity_score - issue_penalty)

    return {
        "suggestions": suggestions,
        "quality_score": round(quality_score, 2)
    }


def register_code_review_tools() -> None:
    """
    (1.) Registers all code review handlers
    (2.) Makes them available for workflow execution
    """
    tool_registry.register("extract_functions", extract_functions)
    tool_registry.register("check_complexity", check_complexity)
    tool_registry.register("detect_issues", detect_issues)
    tool_registry.register("suggest_improvements", suggest_improvements)


def create_code_review_workflow(threshold: float = 70.0) -> GraphConfig:
    """
    (1.) Creates code review workflow configuration
    (2.) Loops until quality_score meets threshold
    """
    return GraphConfig(
        name="code_review",
        nodes=[
            NodeConfig(
                name="extract",
                handler="extract_functions",
                description="Extract function definitions from code"
            ),
            NodeConfig(
                name="complexity",
                handler="check_complexity",
                description="Calculate code complexity score"
            ),
            NodeConfig(
                name="issues",
                handler="detect_issues",
                description="Detect code issues"
            ),
            NodeConfig(
                name="improve",
                handler="suggest_improvements",
                description="Generate improvement suggestions"
            ),
        ],
        edges=[
            EdgeConfig(source="extract", target="complexity"),
            EdgeConfig(source="complexity", target="issues"),
            EdgeConfig(source="issues", target="improve"),
            # (1.) Loop back if quality score below threshold
            # (2.) Re-analyze after improvements suggested
            EdgeConfig(
                source="improve",
                target="complexity",
                condition=ConditionConfig(
                    field="quality_score",
                    operator="lt",
                    value=threshold
                )
            ),
        ],
        entry_node="extract",
        loops={
            "improve": LoopConfig(
                condition=ConditionConfig(
                    field="quality_score",
                    operator="lt",
                    value=threshold
                ),
                max_iterations=5
            )
        }
    )
