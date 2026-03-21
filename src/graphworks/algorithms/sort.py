
from src.graphworks.graph import Graph


def topological(graph: Graph) -> list[str]:
    """
    O(V+E)
    :param graph:
    :return: List of vertices sorted topologically
    """
    def mark_visited(g: Graph, v: str, v_map: dict[str, bool], t_sort_results: list[str]):
        v_map[v] = True
        for n in g.get_neighbors(v):
            if not v_map[n]:
                mark_visited(g, n, v_map, t_sort_results)
        t_sort_results.append(v)

    visited = dict.fromkeys(graph.vertices(), False)
    result: list[str] = []

    for v in graph.vertices():
        if not visited[v]:
            mark_visited(graph, v, visited, result)

    # Contains topo sort results in reverse order
    return result[::-1]
