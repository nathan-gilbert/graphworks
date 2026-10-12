"""Graph traversal algorithms.

Provides breadth-first search and depth-first search.  All functions are pure — they take a
:class:`~graphworks.graph.Graph` and return results without modifying the input.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph


def breadth_first_search(graph: Graph, start: str) -> list[str]:
    """Return vertices reachable from *start* in breadth-first order.

    :param graph: The graph to traverse.
    :type graph: Graph
    :param start: The vertex to begin the traversal from.
    :type start: str
    :return: List of vertex names in BFS visit order.
    :rtype: list[str]
    :raises KeyError: If *start* is not in the graph.
    """
    visited = dict.fromkeys(graph.vertices(), False)
    visited[start] = True

    queue = [start]
    walk: list[str] = []
    while queue:
        cur = queue.pop(0)
        walk.append(cur)

        for i in graph[cur]:
            if not visited[i]:
                queue.append(i)
                visited[i] = True
    return walk


def depth_first_search(graph: Graph, start: str) -> list[str]:
    """Return vertices reachable from *start* in depth-first order.

    :param graph: The graph to traverse.
    :type graph: Graph
    :param start: The vertex to begin the traversal from.
    :type start: str
    :return: List of vertex names in DFS visit order.
    :rtype: list[str]
    :raises KeyError: If *start* is not in the graph.
    """
    visited: list[str] = []
    stack = [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.append(vertex)
            stack.extend(
                filter(lambda x: x not in visited, graph[vertex]),
            )
    return visited
