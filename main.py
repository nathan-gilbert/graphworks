import json

from graphworks.algorithms.basic import find_isolated_vertices
from graphworks.algorithms.basic import generate_edges
from graphworks.export.graphviz import save_to_dot
from graphworks.export.json import save_to_json
from graphworks.graph import Graph

if __name__ == "__main__":
    json_graph = {"label": "my graph", "edges": {"A": ["B"], "B": []}}
    graph = Graph("my graph", input_graph=json.dumps(json_graph))
    print(graph)

    all_edges = generate_edges(graph)
    print(all_edges)

    isolated = find_isolated_vertices(graph)
    print(isolated)

    print("Vertices of graph:")
    print(graph.vertices())

    print("Edges of graph:")
    print(graph.edges())

    print("Add vertex:")
    graph.add_vertex("D")

    print("Vertices of graph:")
    print(graph.vertices())

    print("Add an edge:")
    graph.add_edge("A", "D")

    print("Vertices of graph:")
    print(graph.vertices())

    print("Edges of graph:")
    print(graph.edges())

    graph.add_edge("X", "Y")
    print("Vertices of graph:")
    print(graph.vertices())
    print("Edges of graph:")
    print(graph.edges())

    save_to_dot(graph, ".")
    save_to_json(graph, ".")
