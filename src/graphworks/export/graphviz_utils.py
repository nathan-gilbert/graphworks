from os import path

from graphviz import Graph as GraphViz

from src.graphworks.graph import Graph


def save_to_dot(graph: Graph, out_dir: str):
    """

    :param graph: the graph to render in dot
    :param out_dir: the absolute path of the gv file to write
    :return:
    """
    if not graph.is_directed():
        dot = GraphViz(comment=graph.get_label())
        for node in graph:
            dot.node(node, node)
            for edge in graph[node]:
                dot.edge(node, edge)

        dot.render(path.join(out_dir, f"{graph.get_label()}.gv"), view=False)
