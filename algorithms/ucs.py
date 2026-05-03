"""Uniform Cost Search (UCS) implementation."""

import heapq
from typing import List, Set, Tuple, TypedDict

from base_model import Graph, Node  # noqa: F401


class SearchResult(TypedDict):
    """Standardized output for search algorithms."""

    exploration_order: List[str]
    final_path: List[str]
    total_cost: float


def run_ucs(
    graph: Graph,
    start_node_id: str,
    goal_node_ids: List[str],
) -> SearchResult:
    """Run Uniform Cost Search from a start node to any goal node.

    Args:
        graph: Graph containing nodes and weighted edges.
        start_node_id: ID of the start node.
        goal_node_ids: Candidate goal node IDs; search stops at first reached.

    Returns:
        Standardized "Standard 3" output dictionary containing:
            - exploration_order: node IDs in pop order from priority queue.
            - final_path: shortest path node IDs from start to found goal.
            - total_cost: cumulative path cost for final_path.
    """
    result: SearchResult = {
        "exploration_order": [],
        "final_path": [],
        "total_cost": 0.0,
    }

    if start_node_id not in graph.nodes:
        return result

    goal_set: Set[str] = set(goal_node_ids)
    if not goal_set:
        return result

    priority_queue: List[Tuple[float, str, List[str]]] = [(0.0, start_node_id, [start_node_id])]
    best_cost: Dict[str, float] = {start_node_id: 0.0}

    while priority_queue:
        current_cost, current_node, current_path = heapq.heappop(priority_queue)

        if current_cost > best_cost.get(current_node, float("inf")):
            continue

        result["exploration_order"].append(current_node)

        if current_node in goal_set:
            result["final_path"] = current_path
            result["total_cost"] = current_cost
            return result

        for neighbor_id, edge_weight in graph.get_neighbors(current_node):
            next_cost = current_cost + edge_weight
            if next_cost < best_cost.get(neighbor_id, float("inf")):
                best_cost[neighbor_id] = next_cost
                heapq.heappush(
                    priority_queue,
                    (next_cost, neighbor_id, current_path + [neighbor_id]),
                )

    return result
