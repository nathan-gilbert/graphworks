import sys
from typing import Any
from typing import List
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


def min_degree(graph):
    """ the minimum degree of the vertices """
    minimum = sys.maxsize
    for vertex in graph:
        degree = vertex_degree(graph, vertex)
        if degree < minimum:
            minimum = degree
    return minimum


def max_degree(graph):
    """ the maximum degree of the vertices """
    maximum = 0
    for vertex in graph:
        maximum_degree = vertex_degree(graph, vertex)
        if maximum_degree > maximum:
            maximum = maximum_degree
    return maximum


def degree_sequence(graph):
    seq = []
    for vertex in graph:
        seq.append(vertex_degree(graph, vertex))
    seq.sort(reverse=True)
    return tuple(seq)


def is_degree_sequence(sequence):
    """
    Method returns True, if the sequence is a degree sequence, i.e. a
    non-increasing sequence. Otherwise False.
    :param sequence:
    :return:
    """
    # check if the sequence sequence is non-increasing:
    return all(x >= y for x, y in zip(sequence, sequence[1:]))


def is_erdos_gallai(dsequence):
    """
    Checks if the condition of the Erdoes-Gallai inequality is fulfilled.
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


def density(graph):
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
