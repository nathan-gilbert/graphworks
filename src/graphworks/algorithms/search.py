"""Graph traversal algorithms.

Provides breadth-first search, depth-first search, and a DFS variant that records arrival and
departure timestamps for each vertex.  All functions are pure — they take a
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


def arrival_departure_dfs(  # noqa: PLR0913
    graph: Graph,
    v: str,
    discovered: dict[str, bool],
    arrival: dict[str, int],
    departure: dict[str, int],
    time: int,
) -> int:
    """Perform DFS recording arrival and departure times for each vertex.

    This variant is used internally by :func:`~graphworks.algorithms.directed.is_dag` to detect
    back-edges.  Complexity: O(V + E).

    :param graph: The graph to traverse.
    :type graph: Graph
    :param v: The vertex to traverse from.
    :type v: str
    :param discovered: Mutable map tracking which vertices have been visited.
    :type discovered: dict[str, bool]
    :param arrival: Mutable map storing each vertex's arrival timestamp.
    :type arrival: dict[str, int]
    :param departure: Mutable map storing each vertex's departure timestamp.
    :type departure: dict[str, int]
    :param time: Current timestamp counter (typically initialized to ``-1``).
    :type time: int
    :return: The updated timestamp counter after this subtree is fully explored.
    :rtype: int
    """
    time += 1
    arrival[v] = time
    discovered[v] = True

    for n in graph.neighbors(v):
        if not discovered.get(n, False):
            time = arrival_departure_dfs(
                graph,
                n,
                discovered,
                arrival,
                departure,
                time,
            )

    time += 1
    departure[v] = time
    return time
