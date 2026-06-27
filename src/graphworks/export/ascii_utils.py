r"""Two-dimensional ASCII art rendering of graphworks graphs.

Where ``to_text`` draws a graph as an indented tree, :func:`to_ascii` lays vertices out in 2-D
space and draws edges as lines on a character grid — the "boxes and lines" view.

Layout strategy
---------------
* **DAGs** use a layered (Sugiyama-style) layout: each vertex is placed in a row equal to its
  longest path from a source, reusing :func:`~graphworks.algorithms.sort.topological`.
* **Cyclic or undirected** graphs fall back to a deterministic circular layout.

.. note::

   This is a deliberately simple **first cut**.  Edges are routed as naive straight lines via
   Bresenham's algorithm, so dense graphs will show crossings and overlap.  Planned refinements:
   crossing minimization (barycenter ordering within layers), orthogonal/edge-routed connectors,
   self-loop rendering, and an optional high-resolution braille canvas.  The public surface
   (:func:`to_ascii`) is stable; the rendered output is expected to improve.

Example::

    >>> from graphworks import Graph
    >>> g = Graph("flow", directed=True)
    >>> g.add_edges([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
    Graph('flow', order=4, size=4)
    >>> print(to_ascii(g))  # doctest: +SKIP
    flow
    A
    |\\
    | C
    B |
     \\|
      D
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..algorithms.directed import is_dag
from ..algorithms.sort import topological

if TYPE_CHECKING:
    from ..graph import Graph

# Pixel spacing applied when mapping logical layout cells onto the canvas.
_X_GAP_PAD = 3  # horizontal gap added to the widest label
_Y_GAP = 2  # blank row between layout rows, leaving space for edges


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


def to_ascii(graph: Graph) -> str:
    """Render *graph* as 2-D ASCII art with vertices placed in a plane and edges drawn as lines.

    DAGs are laid out top-down by layer; cyclic and undirected graphs use a circular layout.
    The first line is the graph label (or ``"graph"``).  See the module docstring for the current
    limitations of edge routing.

    :param graph: The graph to render.
    :type graph: Graph
    :return: A multi-line string suitable for printing to a terminal.
    :rtype: str
    """
    root_token = graph.label or "graph"
    if graph.order == 0:
        return f"{root_token}\n(empty graph)"

    cells = _layered_cells(graph) if is_dag(graph) else _circular_cells(graph)
    canvas = _draw(graph, cells)
    return f"{root_token}\n{canvas.render()}"


def _layered_cells(graph: Graph) -> dict[str, tuple[int, int]]:
    """Assign each vertex an integer ``(col, row)`` cell using a longest-path layering.

    Row is the longest path from any source; vertices sharing a row are packed left-to-right in
    insertion order.

    :param graph: A directed acyclic graph.
    :type graph: Graph
    :return: Mapping of vertex name to ``(col, row)`` layout cell.
    :rtype: dict[str, tuple[int, int]]
    """
    layer = dict.fromkeys(graph.vertices(), 0)
    for u in topological(graph):
        base = layer[u] + 1
        for w in graph.neighbors(u):
            layer[w] = max(layer[w], base)

    width_used: dict[int, int] = {}
    cells: dict[str, tuple[int, int]] = {}
    for v in graph.vertices():
        row = layer[v]
        col = width_used.get(row, 0)
        width_used[row] = col + 1
        cells[v] = (col, row)
    return cells


def _circular_cells(graph: Graph) -> dict[str, tuple[int, int]]:
    """Place vertices evenly on a circle and quantize to integer cells.

    The radius grows with vertex count to keep neighbours from colliding.  Rows are squashed
    relative to columns to compensate for terminal characters being taller than they are wide.

    :param graph: The graph to lay out.
    :type graph: Graph
    :return: Mapping of vertex name to ``(col, row)`` layout cell.
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


def _draw(graph: Graph, cells: dict[str, tuple[int, int]]) -> _Canvas:
    """Build and populate a canvas from layout *cells*: edges first, labels on top.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param cells: Mapping of vertex name to ``(col, row)`` layout cell.
    :type cells: dict[str, tuple[int, int]]
    :return: The populated canvas.
    :rtype: _Canvas
    """
    label_width = max(len(v) for v in graph.vertices())
    x_gap = label_width + _X_GAP_PAD
    min_col = min(c for c, _ in cells.values())
    min_row = min(r for _, r in cells.values())

    anchors = {
        v: ((col - min_col) * x_gap, (row - min_row) * _Y_GAP) for v, (col, row) in cells.items()
    }
    width = max(px for px, _ in anchors.values()) + label_width + 1
    height = max(py for _, py in anchors.values()) + 1

    canvas = _Canvas(width, height)
    _draw_edges(canvas, graph, anchors)
    _draw_labels(canvas, anchors)
    return canvas


def _draw_edges(
    canvas: _Canvas,
    graph: Graph,
    anchors: dict[str, tuple[int, int]],
) -> None:
    """Draw every edge once as a straight line between vertex-label centres.

    Self-loops are skipped (not yet supported); undirected edges are drawn a single time.

    :param canvas: The canvas to draw on.
    :type canvas: _Canvas
    :param graph: The graph being rendered.
    :type graph: Graph
    :param anchors: Mapping of vertex name to its top-left pixel anchor.
    :type anchors: dict[str, tuple[int, int]]
    :return: Nothing.
    :rtype: None
    """
    drawn: set[tuple[str, str]] = set()
    for u in graph.vertices():
        for w in graph.neighbors(u):
            if u == w:
                continue
            key = (u, w) if graph.directed else (min(u, w), max(u, w))
            if key in drawn:
                continue
            drawn.add(key)
            ux, uy = _centre(u, anchors)
            wx, wy = _centre(w, anchors)
            canvas.line(ux, uy, wx, wy)


def _draw_labels(canvas: _Canvas, anchors: dict[str, tuple[int, int]]) -> None:
    """Stamp each vertex name at its anchor, over any edge glyphs already drawn.

    :param canvas: The canvas to draw on.
    :type canvas: _Canvas
    :param anchors: Mapping of vertex name to its top-left pixel anchor.
    :type anchors: dict[str, tuple[int, int]]
    :return: Nothing.
    :rtype: None
    """
    for name, (px, py) in anchors.items():
        canvas.text(px, py, name)


def _centre(name: str, anchors: dict[str, tuple[int, int]]) -> tuple[int, int]:
    """Return the approximate centre pixel of *name*'s label.

    :param name: Vertex name.
    :type name: str
    :param anchors: Mapping of vertex name to its top-left pixel anchor.
    :type anchors: dict[str, tuple[int, int]]
    :return: The ``(x, y)`` centre of the label.
    :rtype: tuple[int, int]
    """
    px, py = anchors[name]
    return px + len(name) // 2, py


def _line_glyph(dx: int, dy: int) -> str:
    r"""Pick a line character matching the dominant direction of travel.

    :param dx: Horizontal delta (end minus start).
    :type dx: int
    :param dy: Vertical delta (end minus start).
    :type dy: int
    :return: One of ``-``, ``|``, ``\\`` or ``/``.
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
