"""Core graph data structures for search algorithms.

This module contains the shared Node and Graph classes used by all search
strategy implementations in the project.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Node:
    """Represents a graph node with optional GUI position and heuristic."""

    node_id: str
    pos: Tuple[float, float]
    heuristic: float = 0.0


class Graph:
    """Adjacency-list graph structure storing weighted edges."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.adjacency_list: Dict[str, List[Tuple[str, float]]] = {}

    def add_node(
        self,
        node_id: str,
        pos: Tuple[float, float],
        heuristic: float = 0.0,
    ) -> None:
        """Add or replace a node and ensure it exists in adjacency list."""
        self.nodes[node_id] = Node(node_id=node_id, pos=pos, heuristic=heuristic)
        self.adjacency_list.setdefault(node_id, [])

    def add_edge(
        self,
        u: str,
        v: str,
        weight: float,
        directed: bool = False,
    ) -> None:
        """Add a weighted edge.

        Args:
            u: Source node ID.
            v: Destination node ID.
            weight: Edge cost/weight.
            directed: If False, also add reverse edge.

        Raises:
            ValueError: If either node ID does not exist.
        """
        if u not in self.nodes or v not in self.nodes:
            raise ValueError(
                "Both nodes must exist before adding an edge. "
                f"Missing: {[n for n in (u, v) if n not in self.nodes]}"
            )

        self.adjacency_list.setdefault(u, []).append((v, float(weight)))

        if not directed:
            self.adjacency_list.setdefault(v, []).append((u, float(weight)))

    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        """Return weighted neighbors as (neighbor_id, weight) tuples."""
        return self.adjacency_list.get(node_id, [])
