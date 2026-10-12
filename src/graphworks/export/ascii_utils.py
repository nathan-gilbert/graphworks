r"""Two-dimensional ASCII art rendering of graphworks graphs.

Where ``to_text`` draws a graph as an indented tree, :func:`to_ascii` lays vertices out in 2-D
space and draws edges as lines on a character grid — the "boxes and lines" view.

Layout strategy
---------------
* **DAGs** use a layered (Sugiyama-style) layout:

  1. *Layer assignment* — each vertex's row is its longest path from a source, reusing
     :func:`~graphworks.algorithms.sort.topological_sort`.
  2. *Dummy nodes* — an edge spanning multiple rows is split into unit-length segments through
     virtual nodes in the intervening rows, so it routes as a chain of short lines instead of one
     long diagonal slashing across the layout.
  3. *Ordering* — the left-to-right order within each row is refined by the **barycenter
     heuristic** (iterative up/down sweeps, keeping the ordering with the fewest edge crossings).

* **Cyclic or undirected** graphs fall back to a deterministic circular layout.

.. note::

   Edge segments are still drawn as straight Bresenham lines (with slope-appropriate glyphs)
   rather than orthogonal box-drawing connectors.  Remaining refinements: orthogonal/corner
   routing, horizontal-coordinate assignment (Brandes–Köpf) for straighter chains, a force-
   directed layout for the cyclic/undirected case, self-loop rendering, and a braille canvas.
   The public surface (:func:`to_ascii`) is stable; the rendered output is expected to improve.

Example::

    >>> from graphworks import Graph
    >>> g = Graph("flow", directed=True)
    >>> g.add_edges([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
    Graph('flow', order=4, size=4)
    >>> print(to_ascii(g))  # doctest: +SKIP
    flow
    A
    |\
    B C
    | /
    D
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..algorithms.directed import is_dag
from ..algorithms.sort import topological_sort
from ._labels import RenderStyle, edge_annotation, vertex_text

if TYPE_CHECKING:
    from ..graph import Graph

# Pixel spacing applied when mapping logical layout cells onto the canvas.
_X_GAP_PAD = 3  # horizontal gap added to the widest label
_Y_GAP = 2  # blank row between layout rows, leaving space for edges

# Number of barycenter down+up sweeps when ordering layered graphs.
_SWEEPS = 4

# Prefix marking a routing-only dummy node (never a real vertex name).
_DUMMY = "\x00d"


class _Canvas:
    """A fixed-size grid of characters supporting text and line drawing.

    Coordinates are ``(x, y)`` with the origin at the top-left; out-of-bounds writes are
    silently ignored so callers need not clip.
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a blank canvas at least ``1 x 1`` in size.

        :param width: Desired width in characters.
        :type width: int
        :param height: Desired height in characters.
        :type height: int
        """
        self._width = max(width, 1)
        self._height = max(height, 1)
        self._grid: list[list[str]] = [[" "] * self._width for _ in range(self._height)]

    def put(self, x: int, y: int, char: str) -> None:
        """Write a single character at ``(x, y)`` if it lies on the canvas.

        :param x: Column index.
        :type x: int
        :param y: Row index.
        :type y: int
        :param char: The character to write.
        :type char: str
        :return: Nothing.
        :rtype: None
        """
        if 0 <= x < self._width and 0 <= y < self._height:
            self._grid[y][x] = char

    def text(self, x: int, y: int, label: str) -> None:
        """Write *label* left-to-right starting at ``(x, y)``.

        :param x: Starting column index.
        :type x: int
        :param y: Row index.
        :type y: int
        :param label: The string to stamp.
        :type label: str
        :return: Nothing.
        :rtype: None
        """
        for offset, char in enumerate(label):
            self.put(x + offset, y, char)

    def line(self, x0: int, y0: int, x1: int, y1: int) -> None:
        """Draw a straight line between two points using a slope-appropriate glyph.

        :param x0: Start column.
        :type x0: int
        :param y0: Start row.
        :type y0: int
        :param x1: End column.
        :type x1: int
        :param y1: End row.
        :type y1: int
        :return: Nothing.
        :rtype: None
        """
        glyph = _line_glyph(x1 - x0, y1 - y0)
        for x, y in _bresenham(x0, y0, x1, y1):
            self.put(x, y, glyph)

    def render(self) -> str:
        """Return the canvas as a string, trailing whitespace trimmed per row.

        :return: The rendered grid.
        :rtype: str
        """
        return "\n".join("".join(row).rstrip() for row in self._grid)


@dataclass(frozen=True, slots=True)
class _Plot:
    """A fully positioned layout ready to rasterise onto a :class:`_Canvas`.

    :param ports: Each node id mapped to the pixel ``(x, y)`` it connects through.
    :type ports: dict[str, tuple[int, int]]
    :param labels: Each node id mapped to its display text (``""`` for routing dummies).
    :type labels: dict[str, str]
    :param links: Segment endpoints ``(a, b)`` to draw as lines.
    :type links: list[tuple[str, str]]
    :param notes: Edge annotations to stamp, as ``(x, y, text)``.
    :type notes: list[tuple[int, int, str]]
    """

    ports: dict[str, tuple[int, int]]
    labels: dict[str, str]
    links: list[tuple[str, str]]
    notes: list[tuple[int, int, str]]


def to_ascii(
    graph: Graph,
    *,
    vertex_labels: bool = True,
    edge_labels: bool = True,
    weights: bool | None = None,
) -> str:
    """Render *graph* as 2-D ASCII art with vertices placed in a plane and edges drawn as lines.

    DAGs are laid out top-down by layer with barycenter ordering; cyclic and undirected graphs use
    a circular layout.  The first line is the graph label (or ``"graph"``).

    Vertex labels are shown inside the node text; edge labels and weights are stamped at the edge
    midpoint as ``label, w=…``.  All three are on by default and backward-compatible.

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
    plot = _layered_layout(graph, style) if is_dag(graph) else _circular_layout(graph, style)
    return f"{root_token}\n{_render(plot)}"


# ---------------------------------------------------------------------------
# Layered (Sugiyama) layout for DAGs
# ---------------------------------------------------------------------------


def _layered_layout(graph: Graph, style: RenderStyle) -> _Plot:
    """Build a layered, barycenter-ordered layout for a directed acyclic *graph*.

    :param graph: A directed acyclic graph.
    :type graph: Graph
    :param style: The active display toggles.
    :type style: RenderStyle
    :return: The positioned layout.
    :rtype: _Plot
    """
    layer_of = _assign_layers(graph)
    layers, segments, chains = _expand_with_dummies(graph, layer_of)
    _order_layers(layers, segments)

    labels = {nid: _node_label(graph, nid, style) for layer in layers for nid in layer}
    x_gap = _x_gap(labels)
    ports = _build_ports(layers, x_gap)
    notes = _chain_notes(graph, chains, ports, style)
    return _Plot(ports=ports, labels=labels, links=segments, notes=notes)


def _assign_layers(graph: Graph) -> dict[str, int]:
    """Return each vertex's row as its longest path from any source.

    :param graph: A directed acyclic graph.
    :type graph: Graph
    :return: Mapping of vertex name to row index.
    :rtype: dict[str, int]
    """
    layer = dict.fromkeys(graph.vertices(), 0)
    for u in topological_sort(graph):
        base = layer[u] + 1
        for w in graph.neighbors(u):
            layer[w] = max(layer[w], base)
    return layer


def _expand_with_dummies(
    graph: Graph,
    layer_of: dict[str, int],
) -> tuple[list[list[str]], list[tuple[str, str]], list[tuple[str, str, list[str]]]]:
    """Place vertices into rows and split multi-row edges through dummy nodes.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param layer_of: Each vertex's row index.
    :type layer_of: dict[str, int]
    :return: The ordered ``layers``; the unit-length ``segments`` between adjacent rows; and the
        ``chains`` (one ``(source, target, node_ids)`` per original edge) used for annotation.
    :rtype: tuple[list[list[str]], list[tuple[str, str]], list[tuple[str, str, list[str]]]]
    """
    layers: list[list[str]] = [[] for _ in range(max(layer_of.values()) + 1)]
    for v in graph.vertices():
        layers[layer_of[v]].append(v)

    segments: list[tuple[str, str]] = []
    chains: list[tuple[str, str, list[str]]] = []
    counter = 0
    # A DAG has no self-loops (they are back-edges), so every edge runs strictly downward.
    for u in graph.vertices():
        for w in graph.neighbors(u):
            chain = [u]
            for row in range(layer_of[u] + 1, layer_of[w]):
                dummy = f"{_DUMMY}{counter}"
                counter += 1
                layers[row].append(dummy)
                chain.append(dummy)
            chain.append(w)
            chains.append((u, w, chain))
            segments.extend(zip(chain, chain[1:], strict=False))
    return layers, segments, chains


def _order_layers(layers: list[list[str]], segments: list[tuple[str, str]]) -> None:
    """Reorder nodes within each row to reduce edge crossings (barycenter heuristic).

    Runs alternating down/up sweeps and keeps the ordering with the fewest crossings.  *layers* is
    mutated in place.

    :param layers: The rows of node ids, reordered in place.
    :type layers: list[list[str]]
    :param segments: Unit-length connections between adjacent rows.
    :type segments: list[tuple[str, str]]
    :return: Nothing.
    :rtype: None
    """
    if len(layers) < 2:  # noqa: PLR2004
        return

    upward, downward = _adjacency(segments)
    best = [list(layer) for layer in layers]
    best_score = _count_crossings(layers, segments)
    for _ in range(_SWEEPS):
        for row in range(1, len(layers)):
            _sort_layer(layers[row], upward, layers[row - 1])
        for row in range(len(layers) - 2, -1, -1):
            _sort_layer(layers[row], downward, layers[row + 1])
        score = _count_crossings(layers, segments)
        if score < best_score:
            best_score = score
            best = [list(layer) for layer in layers]

    for row, ordered in enumerate(best):
        layers[row][:] = ordered


def _adjacency(
    segments: list[tuple[str, str]],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Return ``(upward, downward)`` neighbor maps from the segment list.

    ``upward[b]`` holds the upper-row endpoints feeding into *b*; ``downward[a]`` holds the
    lower-row endpoints fed from *a*.

    :param segments: Unit-length connections between adjacent rows.
    :type segments: list[tuple[str, str]]
    :return: The upward and downward adjacency maps.
    :rtype: tuple[dict[str, list[str]], dict[str, list[str]]]
    """
    upward: dict[str, list[str]] = defaultdict(list)
    downward: dict[str, list[str]] = defaultdict(list)
    for a, b in segments:
        downward[a].append(b)
        upward[b].append(a)
    return upward, downward


def _sort_layer(layer: list[str], neighbors: dict[str, list[str]], reference: list[str]) -> None:
    """Sort *layer* in place by each node's barycenter over its *reference*-row neighbors.

    Nodes with no neighbor in *reference* keep their current position.

    :param layer: The row to reorder (mutated in place).
    :type layer: list[str]
    :param neighbors: Adjacency map from a node to its *reference*-row neighbors.
    :type neighbors: dict[str, list[str]]
    :param reference: The already-ordered adjacent row supplying positions.
    :type reference: list[str]
    :return: Nothing.
    :rtype: None
    """
    position = {nid: index for index, nid in enumerate(reference)}
    keyed: list[tuple[float, int, str]] = []
    for index, nid in enumerate(layer):
        seen = [position[n] for n in neighbors.get(nid, ()) if n in position]
        key = sum(seen) / len(seen) if seen else float(index)
        keyed.append((key, index, nid))
    keyed.sort()
    layer[:] = [nid for _, _, nid in keyed]


def _count_crossings(layers: list[list[str]], segments: list[tuple[str, str]]) -> int:
    """Return the total number of edge crossings across all adjacent-row boundaries.

    :param layers: The current row orderings.
    :type layers: list[list[str]]
    :param segments: Unit-length connections between adjacent rows.
    :type segments: list[tuple[str, str]]
    :return: The crossing count.
    :rtype: int
    """
    position = {nid: index for layer in layers for index, nid in enumerate(layer)}
    level = {nid: row for row, layer in enumerate(layers) for nid in layer}
    by_boundary: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for a, b in segments:
        by_boundary[level[a]].append((position[a], position[b]))
    return sum(_inversions(pairs) for pairs in by_boundary.values())


def _inversions(pairs: list[tuple[int, int]]) -> int:
    """Count pairs of segments that cross, given their ``(upper_pos, lower_pos)`` endpoints.

    :param pairs: One ``(upper_pos, lower_pos)`` per segment on a single boundary.
    :type pairs: list[tuple[int, int]]
    :return: The number of crossing pairs.
    :rtype: int
    """
    count = 0
    for i in range(len(pairs)):
        a_top, a_bottom = pairs[i]
        for j in range(i + 1, len(pairs)):
            b_top, b_bottom = pairs[j]
            if (a_top - b_top) * (a_bottom - b_bottom) < 0:
                count += 1
    return count


def _build_ports(layers: list[list[str]], x_gap: int) -> dict[str, tuple[int, int]]:
    """Map each node id to its connection pixel from its ``(column, row)`` cell.

    :param layers: The ordered rows of node ids.
    :type layers: list[list[str]]
    :param x_gap: Horizontal pixels per column.
    :type x_gap: int
    :return: Mapping of node id to ``(x, y)`` port pixel.
    :rtype: dict[str, tuple[int, int]]
    """
    ports: dict[str, tuple[int, int]] = {}
    for row, layer in enumerate(layers):
        for column, nid in enumerate(layer):
            ports[nid] = (column * x_gap + x_gap // 2, row * _Y_GAP)
    return ports


def _chain_notes(
    graph: Graph,
    chains: list[tuple[str, str, list[str]]],
    ports: dict[str, tuple[int, int]],
    style: RenderStyle,
) -> list[tuple[int, int, str]]:
    """Build the annotation placements for each edge, at the midpoint of its routed chain.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param chains: One ``(source, target, node_ids)`` per original edge.
    :type chains: list[tuple[str, str, list[str]]]
    :param ports: Node id to port pixel.
    :type ports: dict[str, tuple[int, int]]
    :param style: The active display toggles.
    :type style: RenderStyle
    :return: Annotations as ``(x, y, text)``.
    :rtype: list[tuple[int, int, str]]
    """
    notes: list[tuple[int, int, str]] = []
    for source, target, chain in chains:
        text = edge_annotation(graph, source, target, style=style)
        if not text:
            continue
        ax, ay = ports[chain[0]]
        bx, by = ports[chain[-1]]
        notes.append(((ax + bx) // 2 + 1, (ay + by) // 2, text))
    return notes


# ---------------------------------------------------------------------------
# Circular layout for cyclic / undirected graphs
# ---------------------------------------------------------------------------


def _circular_layout(graph: Graph, style: RenderStyle) -> _Plot:
    """Build a deterministic circular layout for a cyclic or undirected *graph*.

    :param graph: The graph to lay out.
    :type graph: Graph
    :param style: The active display toggles.
    :type style: RenderStyle
    :return: The positioned layout.
    :rtype: _Plot
    """
    cells = _circular_cells(graph)
    labels = {v: vertex_text(graph, v, use_label=style.vertex_labels) for v in graph.vertices()}
    x_gap = _x_gap(labels)
    min_col = min(c for c, _ in cells.values())
    min_row = min(r for _, r in cells.values())
    ports = {
        v: ((col - min_col) * x_gap + x_gap // 2, (row - min_row) * _Y_GAP)
        for v, (col, row) in cells.items()
    }
    links, notes = _edge_links_and_notes(graph, ports, style)
    return _Plot(ports=ports, labels=labels, links=links, notes=notes)


def _circular_cells(graph: Graph) -> dict[str, tuple[int, int]]:
    """Place vertices evenly on a circle and quantize to integer ``(column, row)`` cells.

    The radius grows with vertex count to keep neighbours from colliding.  Rows are squashed
    relative to columns to compensate for terminal characters being taller than they are wide.

    :param graph: The graph to lay out.
    :type graph: Graph
    :return: Mapping of vertex name to ``(column, row)`` cell.
    :rtype: dict[str, tuple[int, int]]
    """
    verts = graph.vertices()
    n = len(verts)
    radius = max(2, (n + 1) // 2)
    cells: dict[str, tuple[int, int]] = {}
    for i, v in enumerate(verts):
        angle = 2 * math.pi * i / n
        col = round(radius + radius * math.cos(angle))
        row = round(radius / 2 + (radius / 2) * math.sin(angle))
        cells[v] = (col, row)
    return cells


def _edge_links_and_notes(
    graph: Graph,
    ports: dict[str, tuple[int, int]],
    style: RenderStyle,
) -> tuple[list[tuple[str, str]], list[tuple[int, int, str]]]:
    """Return each edge once as a direct link plus its midpoint annotation.

    Self-loops are skipped; undirected edges are emitted a single time.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param ports: Vertex name to port pixel.
    :type ports: dict[str, tuple[int, int]]
    :param style: The active display toggles.
    :type style: RenderStyle
    :return: The ``links`` to draw and the ``notes`` to stamp.
    :rtype: tuple[list[tuple[str, str]], list[tuple[int, int, str]]]
    """
    links: list[tuple[str, str]] = []
    notes: list[tuple[int, int, str]] = []
    drawn: set[tuple[str, str]] = set()
    for u in graph.vertices():
        for w in graph.neighbors(u):
            if u == w:
                continue
            key = (u, w) if graph.directed else (min(u, w), max(u, w))
            if key in drawn:
                continue
            drawn.add(key)
            links.append((u, w))
            text = edge_annotation(graph, u, w, style=style)
            if text:
                ax, ay = ports[u]
                bx, by = ports[w]
                notes.append(((ax + bx) // 2 + 1, (ay + by) // 2, text))
    return links, notes


# ---------------------------------------------------------------------------
# Shared helpers and rasterisation
# ---------------------------------------------------------------------------


def _node_label(graph: Graph, nid: str, style: RenderStyle) -> str:
    """Return the display text for node *nid* (``""`` for routing dummies).

    :param graph: The graph being rendered.
    :type graph: Graph
    :param nid: A node id (a real vertex name or a dummy id).
    :type nid: str
    :param style: The active display toggles.
    :type style: RenderStyle
    :return: The label text, or ``""`` for a dummy node.
    :rtype: str
    """
    if nid not in graph:
        return ""
    return vertex_text(graph, nid, use_label=style.vertex_labels)


def _x_gap(labels: dict[str, str]) -> int:
    """Return the horizontal pixels-per-column: the widest label plus padding.

    :param labels: Node id to display text.
    :type labels: dict[str, str]
    :return: The column width in pixels.
    :rtype: int
    """
    widths = [len(text) for text in labels.values() if text]
    return (max(widths) if widths else 1) + _X_GAP_PAD


def _label_x(port_x: int, text: str) -> int:
    """Return the leftmost column at which *text* is centred on *port_x* (clamped to 0).

    :param port_x: The node's port column.
    :type port_x: int
    :param text: The label text.
    :type text: str
    :return: The starting column for the label.
    :rtype: int
    """
    return max(0, port_x - len(text) // 2)


def _render(plot: _Plot) -> str:
    """Rasterise *plot* onto a canvas: links first, then annotations, then labels on top.

    :param plot: The positioned layout.
    :type plot: _Plot
    :return: The rendered grid.
    :rtype: str
    """
    width, height = _plot_size(plot)
    canvas = _Canvas(width, height)
    for a, b in plot.links:
        ax, ay = plot.ports[a]
        bx, by = plot.ports[b]
        canvas.line(ax, ay, bx, by)
    for x, y, text in plot.notes:
        canvas.text(x, y, text)
    for nid, text in plot.labels.items():
        if text:
            px, py = plot.ports[nid]
            canvas.text(_label_x(px, text), py, text)
    return canvas.render()


def _plot_size(plot: _Plot) -> tuple[int, int]:
    """Compute the canvas dimensions needed to fit every port, label, and annotation.

    :param plot: The positioned layout.
    :type plot: _Plot
    :return: The ``(width, height)`` of the canvas.
    :rtype: tuple[int, int]
    """
    width = 1
    height = 1
    for nid, (px, py) in plot.ports.items():
        width = max(width, px + 1)
        height = max(height, py + 1)
        text = plot.labels.get(nid, "")
        if text:
            width = max(width, _label_x(px, text) + len(text) + 1)
    for x, y, text in plot.notes:
        width = max(width, x + len(text) + 1)
        height = max(height, y + 1)
    return width, height


def _line_glyph(dx: int, dy: int) -> str:
    r"""Pick a line character matching the dominant direction of travel.

    :param dx: Horizontal delta (end minus start).
    :type dx: int
    :param dy: Vertical delta (end minus start).
    :type dy: int
    :return: One of ``-``, ``|``, ``\`` or ``/``.
    :rtype: str
    """
    if dx == 0:
        return "|"
    if dy == 0:
        return "-"
    if (dx > 0) == (dy > 0):
        return "\\"
    return "/"


def _bresenham(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Return the integer points on the line from ``(x0, y0)`` to ``(x1, y1)``.

    :param x0: Start column.
    :type x0: int
    :param y0: Start row.
    :type y0: int
    :param x1: End column.
    :type x1: int
    :param y1: End row.
    :type y1: int
    :return: Ordered list of ``(x, y)`` points, endpoints included.
    :rtype: list[tuple[int, int]]
    """
    points: list[tuple[int, int]] = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    step_x = 1 if x0 < x1 else -1
    step_y = 1 if y0 < y1 else -1
    error = dx + dy
    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            return points
        doubled = 2 * error
        if doubled >= dy:
            error += dy
            x += step_x
        if doubled <= dx:
            error += dx
            y += step_y
