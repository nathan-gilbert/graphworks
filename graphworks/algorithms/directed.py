
from graphworks.graph import Graph


def is_dag(graph: Graph) -> bool:
    if not graph.is_directed():
        return False
