"""This module implements DFS with arrival and departure times."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphworks.graph import Graph


def breadth_first_search(graph: Graph, start: str) -> list[str]:
    """Breadth-first search with arrival and departure times.

    :param graph:
    :type graph: Graph
    :param start: the vertex to start the traversal from
    :type start: str
    :return: The list of vertex paths
    :rtype: list[str]
    """
    # Mark all the vertices as not visited
    visited = dict.fromkeys(graph.vertices(), False)
    # Mark the start vertices as visited and enqueue it
    visited[start] = True

    queue = [start]
    walk = []
    while queue:
        cur = queue.pop(0)
        walk.append(cur)

        for i in graph[cur]:
            if not visited[i]:
                queue.append(i)
                visited[i] = True
    return walk


def depth_first_search(graph: Graph, start: str) -> list[str]:
    """Depth-first search with arrival and departure times.

    :param graph:
    :type graph: Graph
    :param start: the vertex to start the traversal from
    :type start: str
    :return: The list of vertex paths
    :rtype: list[str]
    """
    visited, stack = [], [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.append(vertex)
            stack.extend(filter(lambda x: x not in visited, graph[vertex]))
    return visited


def arrival_departure_dfs(
    graph: Graph,
    v: str,
    discovered: dict[str, bool],
    arrival: dict[str, int],
    departure: dict[str, int],
    time: int,
) -> int:
    """Method for DFS with arrival and departure times for each vertex.

    O(V+E) -- E could be as big as V^2

    :param graph: The graph
    :type graph: Graph
    :param v: The vertex to traverse from
    :type v: str
    :param discovered: The discovered vertex
    :type discovered: dict[str, bool]
    :param arrival: The arrival vertex
    :type arrival: dict[str, int]
    :param departure: The departure vertex
    :type departure: dict[str, int]
    :param time: initialized to -1
    :type time: int
    :return: The departure time
    :rtype: int
    """
    time += 1

    # when did we arrive at vertex 'v'?
    arrival[v] = time
    discovered[v] = True

    for n in graph.get_neighbors(v):
        if not discovered.get(n, False):
            time = arrival_departure_dfs(graph, n, discovered, arrival, departure, time)

    time += 1
    # increment time and then set departure
    departure[v] = time
    return time
