"""A* Search implementation."""

import heapq
from typing import Dict, List, Set, Tuple, TypedDict

from base_model import Graph, Node  # noqa: F401


class SearchResult(TypedDict):
    """Standardized output for search algorithms."""

    exploration_order: List[str]
    final_path: List[str]
    total_cost: float


def run_a_star(
    graph: Graph,
    start_node_id: str,
    goal_node_ids: List[str],
) -> SearchResult:
    """Run A* Search from a start node to any goal node."""

    result: SearchResult = {
        "exploration_order": [],
        "final_path": [],
        "total_cost": 0.0,
    }

    # Check if start node exists
    if start_node_id not in graph.nodes:
        return result

    goal_set: Set[str] = set(goal_node_ids)

    # Check if goals exist
    if not goal_set:
        return result

    # Priority Queue:
    # (f_cost, g_cost, current_node, path)
    priority_queue: List[Tuple[float, float, str, List[str]]] = []

    # Heuristic of start node
    start_heuristic = graph.nodes[start_node_id].heuristic

    # Add start node
    heapq.heappush(
        priority_queue,
        (
            start_heuristic,   # f(n)
            0.0,               # g(n)
            start_node_id,
            [start_node_id],
        ),
    )

    # Store best known cost
    best_cost: Dict[str, float] = {
        start_node_id: 0.0
    }

    while priority_queue:

        current_f, current_cost, current_node, current_path = heapq.heappop(
            priority_queue
        )

        # Skip worse paths
        if current_cost > best_cost.get(current_node, float("inf")):
            continue

        # Add to exploration order
        result["exploration_order"].append(current_node)

        # Goal reached
        if current_node in goal_set:
            result["final_path"] = current_path
            result["total_cost"] = current_cost
            return result

        # Explore neighbors
        for neighbor_id, edge_weight in graph.get_neighbors(current_node):

            # g(n)
            g_cost = current_cost + edge_weight

            # h(n)
            h_cost = graph.nodes[neighbor_id].heuristic

            # f(n) = g(n) + h(n)
            f_cost = g_cost + h_cost

            # Better path found
            if g_cost < best_cost.get(neighbor_id, float("inf")):

                best_cost[neighbor_id] = g_cost

                heapq.heappush(
                    priority_queue,
                    (
                        f_cost,
                        g_cost,
                        neighbor_id,
                        current_path + [neighbor_id],
                    ),
                )

    return result