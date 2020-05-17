from graphviz import Graph as GraphViz
from graphworks.graph import Graph


def save_to_dot(g: Graph, out_file: str):
    """

    :param g: the graph to render in dot
    :param out_file: the absolute path of the gv file to write
    :return:
    """
    if not g.is_directed():
        dot = GraphViz(comment=g.get_label())
        for node in g:
            dot.node(node, node)
            for edge in g[node]:
                dot.edge(node, edge)

        dot.render(out_file+".gv", view=False)
