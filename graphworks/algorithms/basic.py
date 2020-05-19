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


def find_isolated_nodes(graph: Graph) -> List[str]:
    isolated = []
    for node in graph:
        if not graph[node]:
            isolated += node
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
