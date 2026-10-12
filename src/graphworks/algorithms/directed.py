"""Directed graph utilities.

Provides DAG detection and Eulerian circuit finding via Hierholzer's algorithm.  All functions
are pure — they take a :class:`~graphworks.graph.Graph` and return results without modifying the
input.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .properties import _degrees
from .sort import _topological_order

if TYPE_CHECKING:
    from ..graph import Graph


def is_dag(graph: Graph) -> bool:
    """Return ``True`` if *graph* is a directed acyclic graph.

    :param graph: The graph to test.
    :type graph: Graph
    :return: ``True`` if the graph is both directed and acyclic.
    :rtype: bool
    """
    return graph.directed and _topological_order(graph) is not None


def find_circuit(graph: Graph) -> list[str]:
    """Find an Eulerian circuit using Hierholzer's algorithm.

    An Eulerian circuit traverses every edge exactly once and returns to its starting vertex.
    The circuit follows edge direction in directed graphs.

    :param graph: The graph to search for an Eulerian circuit.
    :type graph: Graph
    :return: Vertex names along the circuit (first and last are equal), or ``[]`` if the graph
        has no edges.
    :rtype: list[str]
    :raises ValueError: If the graph has no Eulerian circuit.
    """
    edges = graph.edges()
    if not edges:
        return []

    if not _is_balanced(graph):
        msg = "Graph has no Eulerian circuit: vertex degrees are unbalanced."
        raise ValueError(msg)

    remaining = {v: graph.neighbors(v) for v in graph}
    path = [edges[0].source]
    circuit: list[str] = []
    while path:
        current = path[-1]
        if remaining[current]:
            nxt = remaining[current].pop()
            if not graph.directed and nxt != current:
                remaining[nxt].remove(current)
            path.append(nxt)
        else:
            circuit.append(path.pop())

    if len(circuit) != len(edges) + 1:
        msg = "Graph has no Eulerian circuit: its edges are not connected."
        raise ValueError(msg)
    return circuit[::-1]


def _is_balanced(graph: Graph) -> bool:
    """Return whether every vertex satisfies the Eulerian degree condition.

    Directed graphs need in-degree equal to out-degree; undirected graphs need even degree.

    :param graph: The graph to test.
    :type graph: Graph
    :return: ``True`` if the degree condition holds.
    :rtype: bool
    """
    if not graph.directed:
        return all(d % 2 == 0 for d in _degrees(graph).values())
    in_degree = dict.fromkeys(graph.vertices(), 0)
    for edge in graph.edges():
        in_degree[edge.target] += 1
    return all(len(graph[v]) == in_degree[v] for v in graph)
