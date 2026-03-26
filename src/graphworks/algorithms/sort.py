"""Sorting algorithms for directed graphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphworks.graph import Graph


def topological(graph: Graph) -> list[str]:
    """Return a topological ordering of the vertices in *graph*.

    Uses a recursive DFS-based approach.  Complexity: O(V + E).

    :param graph: A directed acyclic graph.
    :type graph: Graph
    :return: List of vertices sorted topologically.
    :rtype: list[str]
    """

    def _mark_visited(
        g: Graph,
        v: str,
        v_map: dict[str, bool],
        result: list[str],
    ) -> None:
        """Recursively mark *v* and its descendants as visited.

        :param g: The graph.
        :type g: Graph
        :param v: Current vertex.
        :type v: str
        :param v_map: Mutable visited-flag map.
        :type v_map: dict[str, bool]
        :param result: Accumulator for the reverse topological order.
        :type result: list[str]
        :return: Nothing.
        :rtype: None
        """
        v_map[v] = True
        for n in g.neighbors(v):
            if not v_map[n]:
                _mark_visited(g, n, v_map, result)
        result.append(v)

    visited = dict.fromkeys(graph.vertices(), False)
    result: list[str] = []

    for v in graph.vertices():
        if not visited[v]:
            _mark_visited(graph, v, visited, result)

    return result[::-1]
