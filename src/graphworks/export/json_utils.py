"""JSON utilities."""

from __future__ import annotations

import json
from os import path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphworks.graph import Graph


def save_to_json(graph: Graph, out_dir: str) -> None:
    """Save to json file.

    :param graph: the graph to write to json
    :type graph: Graph
    :param out_dir: the absolute path to the dir to write the file
    :type out_dir: str
    :return: Nothing
    :rtype: None
    """
    g_dict = {
        "label": graph.get_label(),
        "directed": graph.is_directed(),
        "graph": graph.get_graph(),
    }

    with open(path.join(out_dir, f"{graph.get_label()}.json"), "w", encoding="utf8") as out:
        out.write(json.dumps(g_dict))
