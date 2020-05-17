import json

from graphworks.algorithms.basic import find_isolated_nodes
from graphworks.algorithms.basic import generate_edges
from graphworks.export.graphviz import save_to_dot
from graphworks.export.json import save_to_json
from graphworks.graph import Graph

if __name__ == "__main__":
    json_graph = {"name": "my graph", "edges": {"A": ["B"], "B": []}}
    g = Graph("my graph", input_graph=json.dumps(json_graph))
    print(g)

    all_edges = generate_edges(g)
    print(all_edges)

    isolated = find_isolated_nodes(g)
    print(isolated)

    save_to_dot(g, f"./{g.get_label()}.gv")
    save_to_json(g, f"./{g.get_label()}.json")
