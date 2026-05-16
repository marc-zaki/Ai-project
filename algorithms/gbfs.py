import heapq
from base_model import Graph 


def run_gbfs(graph: Graph, start_node_id: str, goal_node_ids: list[str]) -> dict:
    goal_set = set(goal_node_ids)

    # Priority queue entries: (heuristic, node_id)
    start_h = graph.nodes[start_node_id].heuristic
    frontier = [(start_h, start_node_id)]

    # came_from tracks the parent of each visited node for path reconstruction
    came_from: dict[str, str | None] = {start_node_id: None}

    # cost_so_far tracks the actual edge-cost to reach each node (for total_cost)
    cost_so_far: dict[str, float] = {start_node_id: 0.0}

    exploration_order: list[str] = []

    while frontier:
        _, current = heapq.heappop(frontier)

        exploration_order.append(current)

        # Goal check
        if current in goal_set:
            final_path = _reconstruct_path(came_from, current)
            total_cost = cost_so_far[current]
            return {
                "exploration_order": exploration_order,
                "final_path": final_path,
                "total_cost": total_cost,
            }

        for neighbor_id, edge_weight in graph.get_neighbors(current):
            if neighbor_id not in came_from:
                came_from[neighbor_id] = current
                cost_so_far[neighbor_id] = cost_so_far[current] + edge_weight
                h = graph.nodes[neighbor_id].heuristic
                heapq.heappush(frontier, (h, neighbor_id))

    return {
        "exploration_order": exploration_order,
        "final_path": [],
        "total_cost": 0.0,
    }


def _reconstruct_path(came_from: dict[str, str | None], goal: str) -> list[str]:
    """Trace back from goal to start using came_from map."""
    path = []
    current: str | None = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path