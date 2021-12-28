from typing import List

from graphworks.graph import Graph


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
