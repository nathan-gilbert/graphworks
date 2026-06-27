"""Plain-text (ASCII/Unicode) rendering of graphworks graphs.

Provides :func:`to_text`, a zero-dependency forest renderer that draws a graph as an
indented tree using box-drawing connectors (``├──``, ``└──``), in the spirit of the Unix
``tree`` command.  It works on any graph — directed or undirected, cyclic or acyclic — by
laying out a depth-first spanning forest and marking edges that close a cycle or point back
to an already-shown vertex with a trailing ``...``.

This is the lightweight, deterministic counterpart to the 2-D grid renderer planned for
:mod:`graphworks.export.ascii_utils`; it is ideal for trees and DAGs and for snapshot tests.

Example::

    >>> from graphworks import Graph
    >>> g = Graph("demo")
    >>> g.add_edge("A", "B").add_edge("A", "C").add_edge("B", "D")
    Graph('demo', order=4, size=3)
    >>> print(to_text(g))
    demo
    ├── A
    │   ├── B
    │   │   └── D
    │   └── C
    ├── D ...
    ...
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._labels import RenderStyle, edge_annotation, vertex_text

if TYPE_CHECKING:
    from ..graph import Graph

# Box-drawing connectors.
_TEE = "├── "
_ELBOW = "└── "
_PIPE = "│   "
_SPACE = "    "

# Trailing marker for a vertex whose subtree was already drawn elsewhere
# (a cycle, a shared child, or a self-loop).
_SEEN = " ..."


def to_text(
    graph: Graph,
    *,
    vertex_labels: bool = True,
    edge_labels: bool = True,
    weights: bool | None = None,
) -> str:
    """Render *graph* as an indented tree using box-drawing connectors.

    The graph is drawn as a depth-first spanning forest under a single root line (the graph
    label, or ``"graph"`` if unlabeled).  For directed graphs, vertices with no incoming edges
    are used as roots first; remaining vertices (including those trapped in cycles) seed
    additional roots in insertion order.  For undirected graphs, the first vertex of each
    connected component becomes that component's root and the edge back to a vertex's parent is
    suppressed for readability.

    A vertex reached a second time is shown as a leaf with a trailing ``...`` and its subtree is
    not repeated, so cycles and shared substructure render in finite space.

    Vertex and edge labels and edge weights are shown when present; an edge carrying either is
    annotated as ``[label, w=…]``.  All three are on by default and are backward-compatible — a
    graph with no custom labels and ``weighted=False`` renders identically to the bare structure.

    :param graph: The graph to render.
    :type graph: Graph
    :param vertex_labels: Show each vertex's label when set, falling back to its name.
    :type vertex_labels: bool
    :param edge_labels: Show each edge's label when set.
    :type edge_labels: bool
    :param weights: Show edge weights.  ``None`` follows the graph's ``weighted`` flag;
        ``True``/``False`` force the choice.
    :type weights: bool | None
    :return: A multi-line string suitable for printing to a terminal.
    :rtype: str
    """
    root_token = graph.label or "graph"
    if graph.order == 0:
        return f"{root_token}\n(empty graph)"

    style = RenderStyle(
        vertex_labels=vertex_labels,
        edge_labels=edge_labels,
        weights=weights,
    )
    candidates = _root_candidates(graph)
    roots = _select_roots(graph, candidates)

    lines: list[str] = [root_token]
    visited: set[str] = set()
    last_root = len(roots) - 1
    for idx, root in enumerate(roots):
        _render(graph, root, None, "", idx == last_root, visited, lines, style)
    return "\n".join(lines)


def _root_candidates(graph: Graph) -> list[str]:
    """Return vertices in the order they should be considered as forest roots.

    Directed sources (in-degree 0) come first so DAGs render top-down; all vertices follow in
    insertion order so that cyclic and undirected components are still covered.

    :param graph: The graph being rendered.
    :type graph: Graph
    :return: Candidate root vertex names, best roots first.
    :rtype: list[str]
    """
    verts = graph.vertices()
    if not graph.directed:
        return verts

    indegree = _indegrees(graph)
    sources = [v for v in verts if indegree[v] == 0]
    rest = [v for v in verts if indegree[v] != 0]
    return sources + rest


def _indegrees(graph: Graph) -> dict[str, int]:
    """Return a mapping of each vertex to its number of incoming edges.

    :param graph: The graph being rendered.
    :type graph: Graph
    :return: Vertex name to in-degree count.
    :rtype: dict[str, int]
    """
    indegree = dict.fromkeys(graph.vertices(), 0)
    for src in graph.vertices():
        for tgt in graph.neighbors(src):
            indegree[tgt] += 1
    return indegree


def _select_roots(graph: Graph, candidates: list[str]) -> list[str]:
    """Reduce *candidates* to the actual forest roots via a reachability pass.

    A candidate becomes a root only if it was not already reachable from an earlier root,
    following the same out-neighbor traversal that :func:`_render` uses.  This guarantees every
    vertex is drawn exactly once as a real node and no chosen root is pre-visited.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param candidates: Vertices to consider, in priority order.
    :type candidates: list[str]
    :return: The vertices that seed each tree in the forest.
    :rtype: list[str]
    """
    roots: list[str] = []
    reached: set[str] = set()
    for candidate in candidates:
        if candidate in reached:
            continue
        roots.append(candidate)
        stack = [candidate]
        while stack:
            node = stack.pop()
            if node in reached:
                continue
            reached.add(node)
            stack.extend(graph.neighbors(node))
    return roots


def _render(  # noqa: PLR0913
    graph: Graph,
    node: str,
    parent: str | None,
    prefix: str,
    is_last: bool,
    visited: set[str],
    lines: list[str],
    style: RenderStyle,
) -> None:
    """Append the lines for *node* and its subtree to *lines* (depth-first).

    :param graph: The graph being rendered.
    :type graph: Graph
    :param node: The vertex to draw.
    :type node: str
    :param parent: The vertex *node* was reached from, or ``None`` for a root.  Used to suppress
        the trivial back-edge in undirected graphs and to resolve the incoming edge's annotation.
    :type parent: str | None
    :param prefix: The accumulated indentation string for this depth.
    :type prefix: str
    :param is_last: Whether *node* is the last child of its parent (selects the connector glyph).
    :type is_last: bool
    :param visited: Vertices already drawn; mutated as the forest is built.
    :type visited: set[str]
    :param lines: Output accumulator, mutated in place.
    :type lines: list[str]
    :param style: The active display toggles.
    :type style: RenderStyle
    :return: Nothing.
    :rtype: None
    """
    connector = _ELBOW if is_last else _TEE
    display = vertex_text(graph, node, use_label=style.vertex_labels)
    content = edge_annotation(graph, parent, node, style=style)
    annotation = f" [{content}]" if content else ""

    if node in visited:
        lines.append(f"{prefix}{connector}{display}{annotation}{_SEEN}")
        return

    lines.append(f"{prefix}{connector}{display}{annotation}")
    visited.add(node)

    children = _children(graph, node, parent)
    child_prefix = prefix + (_SPACE if is_last else _PIPE)
    last_child = len(children) - 1
    for idx, child in enumerate(children):
        _render(graph, child, node, child_prefix, idx == last_child, visited, lines, style)


def _children(graph: Graph, node: str, parent: str | None) -> list[str]:
    """Return the out-neighbors of *node* to recurse into.

    In undirected graphs the edge back to *parent* is dropped so the trivial back-reference is
    not redrawn; genuine cycles (which reach a non-parent ancestor) are preserved.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param node: The vertex whose children are requested.
    :type node: str
    :param parent: The vertex *node* was reached from, or ``None`` for a root.
    :type parent: str | None
    :return: The child vertex names, in adjacency order.
    :rtype: list[str]
    """
    if graph.directed or parent is None:
        return graph.neighbors(node)
    return [tgt for tgt in graph.neighbors(node) if tgt != parent]
