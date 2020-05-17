from graphviz import Graph as GraphViz
from graphworks.graph import Graph


def save_to_file(g: Graph):
    if not g.is_directed():
        dot = GraphViz(comment=g.get_label())
        for node in g:
            dot.node(node, node)
            for edge in g[node]:
                dot.edge(node, edge)

        #print(dot.source)
        dot.render("out.gv", view=True)
