"""Sorting algorithms for directed graphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph


def topological_sort(graph: Graph) -> list[str]:
    """Return a topological ordering of the vertices in *graph*.

    Uses a recursive DFS-based approach.  Complexity: O(V + E).

    :param graph: A directed acyclic graph.
    :type graph: Graph
    :return: List of vertices sorted topologically.
    :rtype: list[str]
    :raises ValueError: If *graph* is undirected or contains a cycle.
    """
    if not graph.directed:
        msg = "topological_sort() requires a directed graph."
        raise ValueError(msg)
    order = _topological_order(graph)
    if order is None:
        msg = "topological_sort() requires an acyclic graph; this graph contains a cycle."
        raise ValueError(msg)
    return order


def _topological_order(graph: Graph) -> list[str] | None:
    """Return a topological ordering of *graph*'s out-edges, or ``None`` if there is a cycle.

    :param graph: The graph to order.
    :type graph: Graph
    :return: Vertices in topological order, or ``None`` when a back-edge is found.
    :rtype: list[str] | None
    """
    on_stack: set[str] = set()
    done: set[str] = set()
    result: list[str] = []

    def _visit(v: str) -> bool:
        on_stack.add(v)
        for n in graph.neighbors(v):
            if n in on_stack or (n not in done and not _visit(n)):
                return False
        on_stack.discard(v)
        done.add(v)
        result.append(v)
        return True

    for v in graph.vertices():
        if v not in done and not _visit(v):
            return None
    return result[::-1]
