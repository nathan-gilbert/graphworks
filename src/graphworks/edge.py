from dataclasses import dataclass


@dataclass
class Edge:
    """
    Implementation of graph edge between 2 vertices. An undirected edge is a
    line. A directed edge is an arc or arrow. Supports weighted (float) edges.
    """
    vertex1: str
    vertex2: str
    directed: bool = False
    weight: float = None

    def has_weight(self) -> bool:
        if self.weight is None:
            return False
        return True
