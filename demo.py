# (1.) Demo script for workflow engine
# (2.) Tests the Code Review workflow

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def demo_code_review():
    """
    (1.) Demonstrates Code Review workflow
    (2.) Creates graph and executes with sample code
    """
    print("=== Agent Workflow Engine Demo ===\n")
    
    # (1.) Sample Python code to review
    # (2.) Contains intentional issues for detection
    sample_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        if num > 0:
            total = total + num
    print(total)
    return total

def process_data(data):
    # TODO: implement this
    pass

from math import *
"""

    # (1.) Create workflow graph
    # (2.) Uses Code Review handlers
    print("1. Creating Code Review workflow graph...")
    graph_config = {
        "config": {
            "name": "code_review",
            "nodes": [
                {"name": "extract", "handler": "extract_functions"},
                {"name": "complexity", "handler": "check_complexity"},
                {"name": "issues", "handler": "detect_issues"},
                {"name": "improve", "handler": "suggest_improvements"}
            ],
            "edges": [
                {"source": "extract", "target": "complexity"},
                {"source": "complexity", "target": "issues"},
                {"source": "issues", "target": "improve"}
            ],
            "entry_node": "extract"
        }
    }
    
    response = requests.post(f"{BASE_URL}/graph/create", json=graph_config)
    if response.status_code != 200:
        print(f"Error creating graph: {response.text}")
        return
    
    graph_id = response.json()["graph_id"]
    print(f"✓ Graph created: {graph_id}\n")
    
    # (1.) Execute workflow
    # (2.) Pass sample code in initial state
    print("2. Executing workflow with sample code...")
    run_request = {
        "graph_id": graph_id,
        "initial_state": {
            "code": sample_code
        }
    }
    
    response = requests.post(f"{BASE_URL}/graph/run", json=run_request)
    if response.status_code != 200:
        print(f"Error running workflow: {response.text}")
        return
    
    result = response.json()
    print(f"✓ Workflow completed: {result['run_id']}\n")
    
    # (1.) Display results
    # (2.) Show extracted information
    print("3. Results:")
    print("-" * 50)
    final_state = result["final_state"]
    
    print(f"\nFunctions found: {final_state.get('function_count', 0)}")
    print(f"Functions: {', '.join(final_state.get('functions', []))}")
    
    print(f"\nCode metrics:")
    print(f"  Lines: {final_state.get('line_count', 0)}")
    print(f"  Control statements: {final_state.get('control_count', 0)}")
    print(f"  Complexity score: {final_state.get('complexity_score', 0)}/100")
    
    print(f"\nIssues detected ({final_state.get('issue_count', 0)}):")
    for issue in final_state.get('issues', []):
        print(f"  - {issue}")
    
    print(f"\nSuggestions:")
    for suggestion in final_state.get('suggestions', []):
        print(f"  - {suggestion}")
    
    print(f"\nQuality score: {final_state.get('quality_score', 0)}/100")
    
    # (1.) Show execution log
    # (2.) Display node execution order
    print("\n4. Execution log:")
    print("-" * 50)
    for log in result["execution_log"]:
        print(f"  {log['node']}: {log['duration_ms']:.2f}ms - {log['status']}")
    
    # (1.) Query state endpoint
    # (2.) Demonstrate state retrieval
    print("\n5. Querying run state...")
    response = requests.get(f"{BASE_URL}/graph/state/{result['run_id']}")
    if response.status_code == 200:
        state_data = response.json()
        print(f"✓ Status: {state_data['status']}")
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    try:
        # (1.) Check if server is running
        # (2.) Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Error: Server not responding. Please start with: uvicorn app.main:app --reload")
            exit(1)
        
        demo_code_review()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server.")
        print("Please start the server with: uvicorn app.main:app --reload")
