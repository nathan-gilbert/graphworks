from graph import Graph


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
