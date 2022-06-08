from typing import List, Dict

from src.graphworks.graph import Graph


def breadth_first_search(graph: Graph, start: str) -> List[str]:
    """

    :param graph:
    :param start: the vertex to start the traversal from
    :return:
    """
    # Mark all the vertices as not visited
    visited = {k: False for k in graph.vertices()}
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


def depth_first_search(graph: Graph, start: str) -> List[str]:
    """

    :param graph:
    :param start: the vertex to start the traversal from
    :return:
    """
    visited, stack = [], [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.append(vertex)
            stack.extend(filter(lambda x: x not in visited, graph[vertex]))
    return visited


def arrival_departure_dfs(graph: Graph,
                          v: str,
                          discovered: Dict[str, bool],
                          arrival: Dict[str, int],
                          departure: Dict[str, int],
                          time: int) -> int:
    """
    Method for DFS with arrival and departure times for each vertex

    O(V+E) -- E could be as big as V^2

    :param graph:
    :param v:
    :param discovered:
    :param arrival:
    :param departure:
    :param time: should be initialized to -1
    :return:
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
