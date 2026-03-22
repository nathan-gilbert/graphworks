"""Graphviz utilities."""

from os import path
from typing import TYPE_CHECKING

from graphviz import Graph as GraphViz

if TYPE_CHECKING:
    from graphworks.graph import Graph


def save_to_dot(graph: Graph, out_dir: str) -> None:
    """Save graph to Graphviz dot file.

    :param graph: the graph to render in dot
    :type graph: Graph
    :param out_dir: the absolute path of the gv file to write
    :type out_dir: str
    :return: Nothing
    :rtype: None
    """
    if not graph.is_directed():
        dot = GraphViz(comment=graph.get_label())
        for node in graph:
            dot.node(node, node)
            for edge in graph[node]:
                dot.edge(node, edge)

        dot.render(path.join(out_dir, f"{graph.get_label()}.gv"), view=False)
