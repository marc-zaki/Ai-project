
from collections import deque
from base_model import Graph, Node  # noqa: F401
 
def run_bfs(graph: Graph, start_node_id: str, goal_node_ids: list[str]) -> dict:

    goals = set(goal_node_ids)
    if start_node_id in goals:
        return {
            "exploration_order": [start_node_id],
            "final_path": [start_node_id],
            "total_cost": 0.0,
        }

    exploration_order: list[str] = []
    visited: set[str] = {start_node_id}
 
    # Each queue entry: (current_node_id, path_so_far, cost_so_far)
    queue: deque[tuple[str, list[str], float]] = deque()
    queue.append((start_node_id, [start_node_id], 0.0))

    while queue:
        current_id, path, cost = queue.popleft()
        exploration_order.append(current_id)
 
        for neighbor_id, edge_weight in graph.get_neighbors(current_id):
            if neighbor_id in visited:
                continue
 
            new_path = path + [neighbor_id]
            new_cost = cost + edge_weight
            visited.add(neighbor_id)
 
            # Goal check — stop as soon as we find any goal
            if neighbor_id in goals:
                exploration_order.append(neighbor_id)
                return {
                    "exploration_order": exploration_order,
                    "final_path": new_path,
                    "total_cost": new_cost,
                }
 
            queue.append((neighbor_id, new_path, new_cost))
 
    return {
        "exploration_order": exploration_order,
        "final_path": [],
        "total_cost": 0.0,
    }
