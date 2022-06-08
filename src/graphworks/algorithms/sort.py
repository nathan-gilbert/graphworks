from typing import List, Dict
from src.graphworks.graph import Graph


def topological(graph: Graph) -> List[str]:
    """
    O(V+E)
    :param graph:
    :return: List of vertices sorted topologically
    """
    def mark_visited(g: Graph, v: str, v_map: Dict[str, bool], t_sort_results: List[str]):
        v_map[v] = True
        for n in g.get_neighbors(v):
            if not v_map[n]:
                mark_visited(g, n, v_map, t_sort_results)
        t_sort_results.append(v)

    visited = {v: False for v in graph.vertices()}
    result: List[str] = []

    for v in graph.vertices():
        if not visited[v]:
            mark_visited(graph, v, visited, result)

    # Contains topo sort results in reverse order
    return result[::-1]
