"""Depth-First Search (DFS) implementation."""

from typing import List, Set, Tuple, TypedDict
from base_model import Graph

class SearchResult(TypedDict):
    """Standardized output for search algorithms."""
    exploration_order: List[str]
    final_path: List[str]
    total_cost: float

def run_dfs(
    graph: Graph,
    start_node_id: str,
    goal_node_ids: List[str],
) -> SearchResult:
    """Run Depth-First Search from a start node to any goal node."""
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

    # Stack stores: (current_node, current_path, cumulative_cost)
    stack: List[Tuple[str, List[str], float]] = [(start_node_id, [start_node_id], 0.0)]
    visited: Set[str] = set()

    while stack: # tol ma el stack msh fadya (lsa 3andy nodes momken a5oshaha)
        current, path, cost = stack.pop() # ana fen w get lel node di ezay w cost kam
        
        if current not in visited: # ana get hena abl keda?
            visited.add(current) # da5alt
            
            # ba save eny ana da5alt el node dih (Standard 3 requirement)
            result["exploration_order"].append(current)
            
            if current in goal_set: # hal ana wa2ef fel goal node delwa2ty? law ah return
                result["final_path"] = path
                result["total_cost"] = cost
                return result
            
            # law laa bashof el nodes el 7awalaya
            neighbors = graph.get_neighbors(current)
            
            # esta5demt reverse 3shan ehna LIFO fa ana 3ayz ashof men awel node msh a5er node
            # (Sorting them first ensures consistent alphabetical order before reversing)
            neighbors = sorted(neighbors, key=lambda x: x[0])
            
            for neighbor_id, edge_weight in reversed(neighbors): 
                if neighbor_id not in visited:
                    stack.append((neighbor_id, path + [neighbor_id], cost + edge_weight))
                    
    return result