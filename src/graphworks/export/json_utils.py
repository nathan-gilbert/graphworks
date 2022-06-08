import json
from os import path

from src.graphworks.graph import Graph


def save_to_json(graph: Graph, out_dir):
    """

    :param graph: the graph to write to json
    :param out_dir: the absolute path to the dir to write the file
    :return:
    """
    g_dict = {
        "label": graph.get_label(),
        "directed": graph.is_directed(),
        "graph": graph.get_graph()
    }

    with open(path.join(out_dir, f"{graph.get_label()}.json"), 'w', encoding="utf8") as out:
        out.write(json.dumps(g_dict))
