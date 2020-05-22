import sys
from typing import Any
from typing import List
from typing import Dict
from typing import Set
from typing import Tuple

from graphworks.graph import Graph


def generate_edges(graph: Graph) -> List[Tuple[Any, Any]]:
    edges = []
    for node in graph:
        for neighbour in graph[node]:
            edges.append((node, neighbour))
    return edges


def find_isolated_vertices(graph: Graph) -> List[str]:
    isolated = []
    for vertex in graph:
        if not graph[vertex]:
            isolated += vertex
    return isolated


def find_path(graph: Graph, start_vertex: str, end_vertex: str, path=None) -> List[str]:
    """ find a path from start_vertex to end_vertex in graph """
    if path is None:
        path = []
    path = path + [start_vertex]
    if start_vertex == end_vertex:
        return path
    if start_vertex not in graph:
        return []
    for vertex in graph[start_vertex]:
        if vertex not in path:
            extended_path = find_path(graph, vertex, end_vertex, path)
            if extended_path:
                return extended_path
    return []


def find_all_paths(graph: Graph, start_vertex: str, end_vertex: str, path=None) -> List[str]:
    """ find all paths from start_vertex to end_vertex in graph """
    if path is None:
        path = []

    path = path + [start_vertex]
    if start_vertex == end_vertex:
        return [path]
    if start_vertex not in graph:
        return []
    paths = []
    for vertex in graph[start_vertex]:
        if vertex not in path:
            extended_paths = find_all_paths(graph, vertex, end_vertex, path)
            for ept in extended_paths:
                paths.append(ept)
    return paths


def vertex_degree(graph: Graph, vertex: str) -> int:
    """ The degree of a vertex is the number of edges connecting it,
    i.e. the number of adjacent vertices. Loops are counted double,
    i.e. every occurrence of a vertex in the list of adjacent vertices. """
    adj_vertices = graph[vertex]
    degree = len(adj_vertices) + adj_vertices.count(vertex)
    return degree


def min_degree(graph: Graph) -> int:
    """ the minimum degree of the vertices """
    minimum = sys.maxsize
    for vertex in graph:
        degree = vertex_degree(graph, vertex)
        if degree < minimum:
            minimum = degree
    return minimum


def max_degree(graph: Graph) -> int:
    """ the maximum degree of the vertices """
    maximum = 0
    for vertex in graph:
        maximum_degree = vertex_degree(graph, vertex)
        if maximum_degree > maximum:
            maximum = maximum_degree
    return maximum


def is_regular(graph: Graph) -> bool:
    return min_degree(graph) == max_degree(graph)


def check_for_cycles(graph: Graph, v: str, visited: Dict[str, bool], rec_stack: List[bool]) -> bool:
    visited[v] = True
    rec_stack[graph.vertices().index(v)] = True

    for neighbour in graph[v]:
        if not visited[neighbour]:
            if check_for_cycles(graph, neighbour, visited, rec_stack):
                return True
        elif rec_stack[neighbour]:
            return True

    rec_stack[graph.vertices().index(v)] = False
    return False


def is_simple(graph: Graph) -> bool:
    """
    A simple graph has no loops
    :param graph:
    :return:
    """
    visited = {k: False for k in graph}
    rec_stack = [False] * graph.order()
    for v in graph:
        if not visited[v]:
            if check_for_cycles(graph, v, visited, rec_stack):
                return True
    return False


def degree_sequence(graph: Graph) -> Tuple[int]:
    seq = []
    for vertex in graph:
        seq.append(vertex_degree(graph, vertex))
    seq.sort(reverse=True)
    return tuple(seq)


def is_degree_sequence(sequence: List[int]) -> bool:
    """
    Method returns True, if the sequence is a degree sequence, i.e. a
    non-increasing sequence. Otherwise False.
    :param sequence:
    :return:
    """
    # check if the sequence sequence is non-increasing:
    return all(x >= y for x, y in zip(sequence, sequence[1:]))


def is_erdos_gallai(dsequence: List[int]) -> bool:
    """
    Checks if the condition of the Erdos-Gallai inequality is fulfilled.
    :param dsequence:
    :return:
    """
    if sum(dsequence) % 2:
        # sum of sequence is odd
        return False

    if is_degree_sequence(dsequence):
        for k in range(1, len(dsequence) + 1):
            left = sum(dsequence[:k])
            right = k * (k - 1) + sum([min(x, k) for x in dsequence[k:]])
            if left > right:
                return False
    else:
        # the sequence is increasing
        return False
    return True


def density(graph: Graph) -> float:
    """
    The graph density is defined as the ratio of the number of edges of a given
    graph, and the total number of edges, the graph could have.
    A dense graph is a graph G = (V, E) in which |E| = Θ(|V|^2)
    :param graph:
    :return:
    """
    vertices = len(graph.vertices())
    edges = len(graph.edges())
    return 2.0 * (edges / (vertices * (vertices - 1)))


def is_connected(graph: Graph,
                 start_vertex: str = None,
                 vertices_encountered: Set[str] = None) -> bool:
    """

    :param graph:
    :param start_vertex:
    :param vertices_encountered:
    :return:
    """
    if vertices_encountered is None:
        vertices_encountered = set()
    vertices = graph.vertices()
    if not start_vertex:
        # choose a vertex from graph as a starting point
        start_vertex = vertices[0]
    vertices_encountered.add(start_vertex)
    if len(vertices_encountered) != len(vertices):
        for vertex in graph[start_vertex]:
            if vertex not in vertices_encountered:
                if is_connected(graph, vertex, vertices_encountered):
                    return True
    else:
        return True
    return False


def diameter(graph: Graph) -> int:
    """

    :param graph:
    :return:
    """
    vee = graph.vertices()
    pairs = [(vee[i], vee[j]) for i in range(len(vee) - 1) for j in range(i + 1, len(vee))]
    smallest_paths = []
    for (start, end) in pairs:
        paths = find_all_paths(graph, start, end)
        smallest = sorted(paths, key=len)[0]
        smallest_paths.append(smallest)

    smallest_paths.sort(key=len)
    # longest path is at the end of list,
    # i.e. diameter corresponds to the length of this path
    dia = len(smallest_paths[-1]) - 1
    return dia
