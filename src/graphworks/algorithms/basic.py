import sys
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple

from numpy import invert
from src.graphworks.graph import Graph


def generate_edges(graph: Graph) -> List[Tuple[str, str]]:
    """

    :param graph: input graph instance
    :return: List of string tuples representing the edges in the input graph
    """
    edges = []
    for node in graph:
        for neighbour in graph[node]:
            edges.append((node, neighbour))
    return edges


def find_isolated_vertices(graph: Graph) -> List[str]:
    """

    :param graph:
    :return:
    """
    isolated = []
    for vertex in graph:
        if not graph[vertex]:
            isolated += vertex
    return isolated


def find_path(graph: Graph, start_vertex: str, end_vertex: str, path=None) -> List[str]:
    """
    find a path from start_vertex to end_vertex in graph

    :param graph: input graph
    :param start_vertex: where the path begins
    :param end_vertex: where the path terminates
    :param path: the current path
    :return: list of vertices in the path
    """
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
    """
    find all paths from start_vertex to end_vertex in graph

    :param graph: input graph
    :param start_vertex: where the path begins
    :param end_vertex: where the path terminates
    :param path: the current path
    :return: list of paths between start and end vertex
    """
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
    i.e. every occurrence of a vertex in the list of adjacent vertices.

    :param graph:
    :param vertex:
    :return: the degree of the supplied vertex
    """
    adj_vertices = graph[vertex]
    degree = len(adj_vertices) + adj_vertices.count(vertex)
    return degree


def min_degree(graph: Graph) -> int:
    """

    :param graph: graph instance to analyze
    :return: the minimum degree of all vertices in graph
    """
    minimum = sys.maxsize
    for vertex in graph:
        degree = vertex_degree(graph, vertex)
        if degree < minimum:
            minimum = degree
    return minimum


def max_degree(graph: Graph) -> int:
    """

    :param graph: graph instance to analyze
    :return: the maximum degree of any vertex in graph
    """
    maximum = 0
    for vertex in graph:
        maximum_degree = vertex_degree(graph, vertex)
        if maximum_degree > maximum:
            maximum = maximum_degree
    return maximum


def is_regular(graph: Graph) -> bool:
    """
    A regular graph is a graph where each vertex has the same number of
    neighbors; i.e. every vertex has the same degree.
    :param graph:
    :return: whether or not graph is regular
    """
    return min_degree(graph) == max_degree(graph)


def check_for_cycles(graph: Graph, v: str, visited: Dict[str, bool], rec_stack: List[bool]) -> bool:
    """

    :param graph:
    :param v: vertex to start from
    :param visited: list of visited vertices
    :param rec_stack:
    :return: whether or not the graph contains a cycle
    """
    visited[v] = True
    rec_stack[graph.vertices().index(v)] = True

    for neighbour in graph[v]:
        if not visited.get(neighbour, False):
            if check_for_cycles(graph, neighbour, visited, rec_stack):
                return True
        elif rec_stack[graph.vertices().index(neighbour)]:
            return True

    rec_stack[graph.vertices().index(v)] = False
    return False


def is_simple(graph: Graph) -> bool:
    """
    A simple graph has no cycles
    :param graph:
    :return: whether or not the graph is simple
    """
    visited = {k: False for k in graph}
    rec_stack = [False] * graph.order()
    for v in graph:
        if not visited[v]:
            if check_for_cycles(graph, v, visited, rec_stack):
                return False
    return True


def degree_sequence(graph: Graph) -> Tuple[int]:
    """

    :param graph:
    :return: Tuple of degrees of all vertices, sorted
    """
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
    V = len(graph.vertices())
    E = len(graph.edges())
    return 2.0 * (E / (V**2 - V))


def is_connected(graph: Graph,
                 start_vertex: str = None,
                 vertices_encountered: Set[str] = None) -> bool:
    """
    :param graph:
    :param start_vertex:
    :param vertices_encountered:
    :return: whether or not the graph is connected
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
    :return: length of longest path in graph
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


def is_sparse(graph: Graph) -> bool:
    """
    Checks if |E| <= |V^2| / 2
    :param graph:
    :return:
    """
    return graph.size() <= (graph.order()**2 / 2)


def get_complement(graph: Graph) -> Graph:
    """
    If graph is represented as a matrix, invert that matrix
    :param graph:
    :return: inversion of graph
    """
    adj = graph.get_adjacency_matrix()
    complement = invert(adj)
    return Graph(label=f"{graph.get_label()} complement", input_array=complement)


def is_complete(graph: Graph) -> bool:
    """
    Checks that each vertex has V(V-1) / 2 edges and that each vertex is
    connected to V - 1 others.

    runtime: O(n^2)
    :param graph:
    :return: true or false
    """
    V = len(graph.vertices())
    max_edges = (V**2 - V)
    if not graph.is_directed():
        max_edges //= 2

    E = len(graph.edges())
    if E != max_edges:
        return False

    for vertex in graph:
        if len(graph[vertex]) != V - 1:
            return False
    return True
