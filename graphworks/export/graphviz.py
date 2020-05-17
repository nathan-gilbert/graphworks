from graphviz import Graph as GraphViz
from graphworks.graph import Graph


def save_and_render(g: Graph, out_file: str):
    if not g.is_directed():
        dot = GraphViz(comment=g.get_label())
        for node in g:
            dot.node(node, node)
            for edge in g[node]:
                dot.edge(node, edge)

        dot.render(out_file, view=True)
