"""Directed graph utilities.

Provides DAG detection and Eulerian circuit finding via Hierholzer's algorithm.  All functions
are pure — they take a :class:`~graphworks.graph.Graph` and return results without modifying the
input.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from graphworks.algorithms.search import arrival_departure_dfs

if TYPE_CHECKING:
    from graphworks.graph import Graph


def is_dag(graph: Graph) -> bool:
    """Return ``True`` if *graph* is a directed acyclic graph.

    Uses arrival/departure DFS to detect back-edges.

    :param graph: The graph to test.
    :type graph: Graph
    :return: ``True`` if the graph is both directed and acyclic.
    :rtype: bool
    """
    if not graph.directed:
        return False

    departure = dict.fromkeys(graph.vertices(), 0)
    discovered = dict.fromkeys(graph.vertices(), False)
    arrival = dict.fromkeys(graph.vertices(), 0)
    time = -1

    for n in graph.vertices():
        if not discovered[n]:
            time = arrival_departure_dfs(
                graph,
                n,
                discovered,
                arrival,
                departure,
                time,
            )

    for n in graph.vertices():
        for v in graph.neighbors(n):
            if departure[n] <= departure[v]:
                return False

    return True


def build_neighbor_matrix(graph: Graph) -> dict[str, list[str]]:
    """Build a mutable adjacency dict for *graph*.

    Returns a fresh ``dict[str, list[str]]`` that can be mutated without affecting the original
    graph — used internally by :func:`find_circuit`.

    :param graph: The graph.
    :type graph: Graph
    :return: Mutable adjacency mapping.
    :rtype: dict[str, list[str]]
    """
    return {v: list(graph.neighbors(v)) for v in graph.vertices()}


def find_circuit(graph: Graph) -> list[str]:
    """Find an Eulerian circuit using Hierholzer's algorithm.

    :param graph: The graph to search for an Eulerian circuit.
    :type graph: Graph
    :return: List of vertex names forming the circuit, or ``[]`` if the graph has no vertices.
    :rtype: list[str]
    """
    if len(graph.vertices()) == 0:
        return []

    circuit: list[str] = []
    adjacency_matrix = build_neighbor_matrix(graph)
    current_path: list[str] = [graph.vertices()[0]]
    while len(current_path) > 0:
        current_vertex = current_path[-1]
        if len(adjacency_matrix[current_vertex]) > 0:
            next_vertex = adjacency_matrix[current_vertex].pop()
            current_path.append(next_vertex)
        else:
            circuit.append(current_path.pop())

    return circuit
