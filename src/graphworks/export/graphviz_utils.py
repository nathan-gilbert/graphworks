"""Graphviz DOT export for graphworks graphs.

Provides :func:`save_to_dot` for rendering a
:class:`~graphworks.graph.Graph` as a Graphviz DOT file.  Requires the ``[viz]`` optional extra::

    pip install graphworks[viz]
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from graphviz import Digraph
from graphviz import Graph as UndirectedGraphViz

if TYPE_CHECKING:
    from graphworks.graph import Graph


def save_to_dot(graph: Graph, out_dir: str) -> None:
    """Render *graph* to a Graphviz DOT file in *out_dir*.

    Produces both a ``.gv`` source file and its rendered output.  Directed
    graphs use :class:`graphviz.Digraph`; undirected graphs use
    :class:`graphviz.Graph`.

    :param graph: The graph to render.
    :type graph: Graph
    :param out_dir: Directory path where the DOT file will be written.
    :type out_dir: str
    :return: Nothing.
    :rtype: None
    """
    if graph.directed:
        dot = Digraph(comment=graph.label)
    else:
        dot = UndirectedGraphViz(comment=graph.label)

    for node in graph:
        dot.node(node, node)
        for neighbour in graph[node]:
            dot.edge(node, neighbour)

    dot.render(str(Path(out_dir) / f"{graph.label}.gv"), view=False)
