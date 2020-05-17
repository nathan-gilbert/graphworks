import json

from graphworks.graph import Graph


def save_to_json(graph: Graph, out_file):
    """

    :param graph: the graph to write to json
    :param out_file: the absolute path to write the json file
    :return:
    """
    g_dict = {
        "label": graph.get_label(),
        "directed": graph.is_directed(),
        "edges": graph.edges
    }

    with open(out_file, 'w') as out:
        out.write(json.dumps(g_dict))
