from graphworks.graph import Graph


def generate_edges(graph: Graph) -> list:
    edges = []
    for node in graph:
        for neighbour in graph[node]:
            edges.append((node, neighbour))
    return edges


def find_isolated_nodes(graph) -> list:
    isolated = []
    for node in graph:
        if not graph[node]:
            isolated += node
    return isolated


def find_path(graph: Graph, start_vertex: str, end_vertex: str, path=None):
    """ find a path from start_vertex to end_vertex in graph """
    if path is None:
        path = []
    path = path + [start_vertex]
    if start_vertex == end_vertex:
        return path
    if start_vertex not in graph:
        return None
    for vertex in graph[start_vertex]:
        if vertex not in path:
            extended_path = find_path(graph, vertex, end_vertex, path)
            if extended_path:
                return extended_path
    return None
