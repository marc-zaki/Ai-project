"""Comprehensive validation script for Graph model and UCS behavior.

Run with:
    python test_search.py
"""

from __future__ import annotations

import heapq
from typing import Any

from algorithms.ucs import run_ucs
from base_model import Graph

STANDARD_KEYS = {"exploration_order", "final_path", "total_cost"}


def assert_standard_output_structure(result: Any) -> None:
    """Validate that UCS returns the expected Standard 3 shape."""
    assert isinstance(result, dict), "UCS output must be a dictionary."
    missing_keys = STANDARD_KEYS.difference(result.keys())
    assert not missing_keys, f"Missing Standard 3 keys: {sorted(missing_keys)}"
    assert isinstance(
        result["exploration_order"], list
    ), "'exploration_order' must be a list."
    assert isinstance(result["final_path"], list), "'final_path' must be a list."
    assert isinstance(
        result["total_cost"], (int, float)
    ), "'total_cost' must be numeric."


def build_test_graph() -> Graph:
    """Build a weighted graph with directed and undirected edges."""
    graph = Graph()

    # Add 6 nodes with GUI-style positions.
    graph.add_node("A", (0.0, 0.0), heuristic=7.0)
    graph.add_node("B", (1.0, 0.0), heuristic=6.0)
    graph.add_node("C", (2.0, 0.0), heuristic=5.0)
    graph.add_node("D", (0.0, 1.0), heuristic=4.0)
    graph.add_node("E", (1.0, 1.0), heuristic=2.0)
    graph.add_node("F", (2.0, 1.0), heuristic=0.0)

    # Undirected edges:
    # A-B-F has fewer jumps but is expensive.
    graph.add_edge("A", "B", 6.0, directed=False)
    graph.add_edge("B", "F", 6.0, directed=False)
    graph.add_edge("A", "D", 1.0, directed=False)
    graph.add_edge("D", "E", 1.0, directed=False)
    graph.add_edge("E", "C", 1.0, directed=False)

    # Directed edges:
    # Longer but cheaper route A->D->E->C->F (cost 4.0) beats A->B->F (cost 12.0).
    graph.add_edge("C", "F", 1.0, directed=True)
    graph.add_edge("B", "E", 2.5, directed=True)

    return graph


def compute_min_costs(graph: Graph, start_node_id: str) -> dict[str, float]:
    """Compute minimum cost from start to every reachable node."""
    min_costs: dict[str, float] = {start_node_id: 0.0}
    queue: list[tuple[float, str]] = [(0.0, start_node_id)]

    while queue:
        cost, node = heapq.heappop(queue)
        if cost > min_costs.get(node, float("inf")):
            continue

        for neighbor, weight in graph.get_neighbors(node):
            next_cost = cost + weight
            if next_cost < min_costs.get(neighbor, float("inf")):
                min_costs[neighbor] = next_cost
                heapq.heappush(queue, (next_cost, neighbor))

    return min_costs


def test_single_goal_cheapest_path() -> None:
    """Verify UCS picks mathematically cheapest path, not fewest edges."""
    graph = build_test_graph()
    start_node = "A"
    goal_node = "F"

    result = run_ucs(graph, start_node, [goal_node])
    assert_standard_output_structure(result)

    exploration_order = result["exploration_order"]
    final_path = result["final_path"]
    total_cost = float(result["total_cost"])

    print("\n=== Test 1: Single Goal ===")
    print(f"Exploration order: {exploration_order}")
    print(f"Final path: {final_path}")
    print(f"Total cost: {total_cost}")

    expected_path = ["A", "D", "E", "C", "F"]
    expected_cost = 4.0

    # For UCS with non-negative weights, popped node costs should be non-decreasing.
    min_costs = compute_min_costs(graph, start_node)
    popped_costs = [min_costs[node_id] for node_id in exploration_order]
    assert popped_costs == sorted(popped_costs), (
        "Exploration order should be non-decreasing by cumulative cost."
    )

    # Deterministic verification for this specific graph and insertion order.
    assert exploration_order[:5] == ["A", "D", "E", "C", "F"], (
        "Exploration order should reflect increasing cumulative cost for this "
        "graph setup."
    )
    assert final_path == expected_path, (
        f"Expected cheapest path {expected_path}, got {final_path}"
    )
    assert abs(total_cost - expected_cost) < 1e-9, (
        f"Expected total_cost {expected_cost}, got {total_cost}"
    )


def test_multi_goal_stops_at_cheapest_goal() -> None:
    """Verify UCS returns when it reaches the cheapest goal among candidates."""
    graph = build_test_graph()
    start_node = "A"
    goal_nodes = ["E", "F"]

    result = run_ucs(graph, start_node, goal_nodes)
    assert_standard_output_structure(result)

    exploration_order = result["exploration_order"]
    final_path = result["final_path"]
    total_cost = float(result["total_cost"])

    print("\n=== Test 2: Multi-Goal ===")
    print(f"Exploration order: {exploration_order}")
    print(f"Final path: {final_path}")
    print(f"Total cost: {total_cost}")

    # Cheapest reachable goal from A among {E, F} is E with path A-D-E (cost 2).
    assert final_path == ["A", "D", "E"], (
        "UCS should stop at the cheapest goal among candidates."
    )
    assert abs(total_cost - 2.0) < 1e-9, (
        f"Expected total_cost 2.0 for cheapest goal E, got {total_cost}"
    )
    assert final_path[-1] in goal_nodes, "Final node must be one of the goals."


def main() -> None:
    """Run all UCS validation tests."""
    try:
        test_single_goal_cheapest_path()
        test_multi_goal_stops_at_cheapest_goal()
    except AssertionError as error:
        print(f"\nUCS test failed: {error}")
        raise
    except Exception as error:  # Defensive catch for unexpected runtime issues.
        print(f"\nUnexpected test error: {error}")
        raise

    print("\nAll UCS Tests Passed!")


if __name__ == "__main__":
    main()
