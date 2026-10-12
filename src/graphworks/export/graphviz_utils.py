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

from ..utilities import _file_stem
from ._labels import RenderStyle, edge_annotation, vertex_text

if TYPE_CHECKING:
    from ..graph import Graph


def save_to_dot(graph: Graph, out_dir: str) -> Path:
    """Render *graph* to a Graphviz DOT file in *out_dir*.

    Produces both a ``.gv`` source file and its rendered output, named after
    :attr:`~graphworks.graph.Graph.label` (path separators replaced with ``_``; ``graph.gv`` if
    unlabeled).  Directed graphs use :class:`graphviz.Digraph`; undirected graphs use
    :class:`graphviz.Graph`.  Vertex labels are used as node labels, and edge labels and weights
    are shown as edge labels (``label, w=…``).

    :param graph: The graph to render.
    :type graph: Graph
    :param out_dir: Directory path where the DOT file will be written.
    :type out_dir: str
    :return: Path of the written ``.gv`` source file.
    :rtype: Path
    """
    if graph.directed:
        dot = Digraph(comment=graph.label)
    else:
        dot = UndirectedGraphViz(comment=graph.label)

    style = RenderStyle(weights=True)
    for node in graph:
        dot.node(node, vertex_text(graph, node))
    for edge in graph.edges():
        text = edge_annotation(graph, edge.source, edge.target, style=style)
        dot.edge(edge.source, edge.target, label=text or None)

    out_path = Path(out_dir) / f"{_file_stem(graph.label)}.gv"
    dot.render(str(out_path), view=False)
    return out_path
