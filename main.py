import json
from graphworks.graph import Graph
from graphworks.algorithms.basic import generate_edges, find_isolated_nodes

if __name__ == "__main__":
    json_graph = {"name": "my graph", "edges": {"A": ["B"], "B": []}}
    g = Graph("my graph", input_graph=json.dumps(json_graph))
    print(g)

    all_edges = generate_edges(g)
    print(all_edges)

    isolated = find_isolated_nodes(g)
    print(isolated)
