"""Path-finding and edge-generation utilities.

This module provides functions for discovering paths between vertices,
generating edge lists, and finding structurally isolated vertices.  All
functions operate on the adjacency-list representation and require no
external dependencies.

:author: Nathan Gilbert
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphworks.edge import Edge
    from graphworks.graph import Graph


def generate_edges(graph: Graph) -> list[Edge]:
    """Return all edges in *graph* as a list of :class:`~graphworks.edge.Edge` objects.

    This is a convenience wrapper around :meth:`~graphworks.graph.Graph.edges`.

    :param graph: The graph to enumerate edges from.
    :type graph: Graph
    :return: List of edges.
    :rtype: list[Edge]
    """
    return graph.edges()


def find_isolated_vertices(graph: Graph) -> list[str]:
    """Return vertices that have no neighbours.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: List of vertex names with degree zero.
    :rtype: list[str]
    """
    return [v for v in graph.vertices() if not graph[v]]


def find_path(
    graph: Graph,
    start: str,
    end: str,
    path: list[str] | None = None,
) -> list[str]:
    """Find a single path between *start* and *end* using depth-first search.

    Returns the first path found, not necessarily the shortest.  Returns an
    empty list if no path exists or if *start* is not in the graph.

    :param graph: The graph to search.
    :type graph: Graph
    :param start: Source vertex name.
    :type start: str
    :param end: Destination vertex name.
    :type end: str
    :param path: Accumulated path used by recursive calls.  Callers should
        leave this as ``None``.
    :type path: list[str] | None
    :return: Ordered list of vertex names from *start* to *end*, or ``[]``
        if no path exists.
    :rtype: list[str]
    """
    if path is None:
        path = []

    if start not in graph.vertices():
        return []

    path = [*path, start]

    if start == end:
        return path

    for node in graph[start]:
        if node not in path:
            new_path = find_path(graph, node, end, path)
            if new_path:
                return new_path
    return []


def find_all_paths(
    graph: Graph,
    start: str,
    end: str,
    path: list[str] | None = None,
) -> list[list[str]]:
    """Return all simple paths between *start* and *end*.

    A simple path visits each vertex at most once.  Returns an empty list
    if no path exists or if *start* is not in the graph.

    :param graph: The graph to search.
    :type graph: Graph
    :param start: Source vertex name.
    :type start: str
    :param end: Destination vertex name.
    :type end: str
    :param path: Accumulated path used by recursive calls.  Callers should
        leave this as ``None``.
    :type path: list[str] | None
    :return: List of all simple paths, each path being an ordered list of
        vertex names.
    :rtype: list[list[str]]
    """
    if path is None:
        path = []

    if start not in graph.vertices():
        return []

    path = [*path, start]

    if start == end:
        return [path]

    paths: list[list[str]] = []
    for node in graph[start]:
        if node not in path:
            new_paths = find_all_paths(graph, node, end, path)
            paths.extend(new_paths)
    return paths
