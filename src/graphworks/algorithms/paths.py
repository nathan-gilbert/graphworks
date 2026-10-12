"""Path-finding utilities.

Provides functions for discovering paths between vertices and finding structurally isolated
vertices.  All functions operate on the adjacency-list representation and
require no external dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ..graph import Graph


def find_isolated_vertices(graph: Graph) -> list[str]:
    """Return vertices that have no incident edges (degree zero).

    For directed graphs a vertex with only incoming edges is *not* isolated.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: List of vertex names with degree zero.
    :rtype: list[str]
    """
    touched = {v for edge in graph.edges() for v in (edge.source, edge.target)}
    return [v for v in graph.vertices() if v not in touched]


def find_path(graph: Graph, start: str, end: str) -> list[str]:
    """Find a single path between *start* and *end* using depth-first search.

    Returns the first path found, not necessarily the shortest.

    :param graph: The graph to search.
    :type graph: Graph
    :param start: Source vertex name.
    :type start: str
    :param end: Destination vertex name.
    :type end: str
    :return: Ordered list of vertex names from *start* to *end*, or ``[]`` if no path exists.
    :rtype: list[str]
    :raises KeyError: If *start* or *end* is not in the graph.
    """
    _require_endpoints(graph, start, end)
    paths = _simple_paths(graph, [start], end)
    return next(paths, [])


def find_all_paths(graph: Graph, start: str, end: str) -> list[list[str]]:
    """Return all simple paths between *start* and *end*.

    A simple path visits each vertex at most once.

    :param graph: The graph to search.
    :type graph: Graph
    :param start: Source vertex name.
    :type start: str
    :param end: Destination vertex name.
    :type end: str
    :return: List of all simple paths, each an ordered list of vertex names, or ``[]`` if none.
    :rtype: list[list[str]]
    :raises KeyError: If *start* or *end* is not in the graph.
    """
    _require_endpoints(graph, start, end)
    return list(_simple_paths(graph, [start], end))


def _simple_paths(graph: Graph, path: list[str], end: str) -> Iterator[list[str]]:
    """Yield every simple path that extends *path* to *end*, depth-first.

    :param graph: The graph to search.
    :type graph: Graph
    :param path: The path walked so far (non-empty).
    :type path: list[str]
    :param end: Destination vertex name.
    :type end: str
    :return: Iterator of complete paths.
    :rtype: Iterator[list[str]]
    """
    if path[-1] == end:
        yield path
        return
    for node in graph[path[-1]]:
        if node not in path:
            yield from _simple_paths(graph, [*path, node], end)


def _require_endpoints(graph: Graph, *names: str) -> None:
    """Raise :class:`KeyError` for the first of *names* not in *graph*.

    :param graph: The graph to check.
    :type graph: Graph
    :param names: Vertex names that must exist.
    :type names: str
    :return: Nothing.
    :rtype: None
    :raises KeyError: If a vertex is missing.
    """
    for name in names:
        if name not in graph:
            msg = f"Vertex {name!r} is not in the graph."
            raise KeyError(msg)
