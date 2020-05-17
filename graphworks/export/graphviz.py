from graphviz import Graph as GraphViz

from graphworks.graph import Graph


def save_to_dot(graph: Graph, out_file: str):
    """

    :param graph: the graph to render in dot
    :param out_file: the absolute path of the gv file to write
    :return:
    """
    if not graph.is_directed():
        dot = GraphViz(comment=graph.get_label())
        for node in graph:
            dot.node(node, node)
            for edge in graph[node]:
                dot.edge(node, edge)

        dot.render(out_file + ".gv", view=False)
