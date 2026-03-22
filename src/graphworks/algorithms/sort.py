"""Sorting algorithms."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphworks.graph import Graph


def topological(graph: Graph) -> list[str]:
    """Topological sort.

    O(V+E)

    :param graph:
    :type graph: Graph
    :return: List of vertices sorted topologically
    :rtype: list[str]
    """

    def mark_visited(g: Graph, v: str, v_map: dict[str, bool], t_sort_results: list[str]) -> None:
        """Mark visited vertex as visited.

        :param g: The graphc
        :type g: Graph
        :param v: Vertex
        :type v: str
        :param v_map: Mapping from vertex to vertex index
        :type v_map: dict[str, bool]
        :param t_sort_results: List of vertices sorted topologically
        :type t_sort_results: list[str]
        :return: Nothing
        :rtype: None
        """
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
