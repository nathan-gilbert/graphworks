from graphworks.graph import Graph
import json


def save_to_json(g: Graph, out_file):
    g_dict = {
        "label": g.get_label(),
        "directed": g.is_directed(),
        "edges": g.edges
    }

    with open(out_file, 'w') as out:
        out.write(json.dumps(g_dict))
