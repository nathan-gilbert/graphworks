"""Unit tests for :mod:`graphworks.export.ascii_utils`.

These cover the Phase 2 scaffold: the character canvas primitives and the layout/render pipeline.
Assertions check structure (labels present, determinism, layout shape) rather than exact art, so
the renderer can be refined without churning the suite.
"""

from __future__ import annotations

import json

import pytest

from graphworks.export.ascii_utils import (
    _bresenham,
    _Canvas,
    _line_glyph,
    to_ascii,
)
from graphworks.graph import Graph


class TestCanvas:
    """Primitive drawing operations on the character grid."""

    def test_put_and_render(self) -> None:
        """A single character lands at its coordinate; the rest stays blank."""
        canvas = _Canvas(3, 2)
        canvas.put(1, 0, "x")
        assert canvas.render() == " x\n"

    def test_out_of_bounds_is_ignored(self) -> None:
        """Writes outside the grid are silently dropped."""
        canvas = _Canvas(2, 2)
        canvas.put(-1, 0, "x")
        canvas.put(5, 5, "y")
        assert canvas.render() == "\n"

    def test_text_runs_left_to_right(self) -> None:
        """text() stamps a label one character per column."""
        canvas = _Canvas(5, 1)
        canvas.text(1, 0, "hi")
        assert canvas.render() == " hi"

    def test_minimum_size(self) -> None:
        """A degenerate request still yields a usable 1x1 canvas."""
        assert _Canvas(0, 0).render() == ""

    def test_horizontal_line(self) -> None:
        """A flat line uses the dash glyph."""
        canvas = _Canvas(4, 1)
        canvas.line(0, 0, 3, 0)
        assert canvas.render() == "----"

    def test_vertical_line(self) -> None:
        """A straight drop uses the pipe glyph."""
        canvas = _Canvas(1, 3)
        canvas.line(0, 0, 0, 2)
        assert canvas.render() == "|\n|\n|"

    def test_diagonal_glyphs(self) -> None:
        """Down-right uses backslash; down-left uses forward slash."""
        down_right = _Canvas(3, 3)
        down_right.line(0, 0, 2, 2)
        assert down_right.render().splitlines()[0][0] == "\\"

        down_left = _Canvas(3, 3)
        down_left.line(2, 0, 0, 2)
        assert down_left.render().splitlines()[0][2] == "/"


class TestLineGlyph:
    """Direction-to-glyph mapping."""

    @pytest.mark.parametrize(
        ("dx", "dy", "expected"),
        [
            (0, 5, "|"),
            (5, 0, "-"),
            (3, 4, "\\"),
            (-3, -4, "\\"),
            (3, -4, "/"),
            (-3, 4, "/"),
        ],
    )
    def test_glyph(self, dx: int, dy: int, expected: str) -> None:
        """Each direction maps to the expected line character."""
        assert _line_glyph(dx, dy) == expected


class TestBresenham:
    """The integer line rasteriser."""

    def test_endpoints_included(self) -> None:
        """The returned path starts and ends on the requested points."""
        points = _bresenham(0, 0, 3, 1)
        assert points[0] == (0, 0)
        assert points[-1] == (3, 1)

    def test_single_point(self) -> None:
        """A zero-length line is just its single point."""
        assert _bresenham(2, 2, 2, 2) == [(2, 2)]


class TestToAscii:
    """End-to-end rendering."""

    def test_empty_graph(self) -> None:
        """An empty graph renders the root token and a marker."""
        assert to_ascii(Graph("empty")) == "empty\n(empty graph)"

    def test_label_is_first_line(self) -> None:
        """The label heads the rendering; unlabeled graphs use 'graph'."""
        g = Graph(directed=True)
        g.add_edge("A", "B")
        assert to_ascii(g).splitlines()[0] == "graph"

    def test_dag_contains_every_vertex(self, directed_dag: Graph) -> None:
        """A layered DAG render mentions every vertex."""
        rendered = to_ascii(directed_dag)
        for vertex in directed_dag.vertices():
            assert vertex in rendered

    def test_linear_dag_stacks_vertically(self) -> None:
        """A path A->B->C lays out one vertex per layer, top to bottom."""
        g = Graph("line", directed=True)
        g.add_edges([("A", "B"), ("B", "C")])
        rows = [line.strip() for line in to_ascii(g).splitlines()[1:] if line.strip()]
        assert rows == ["A", "|", "B", "|", "C"]

    def test_cyclic_directed_falls_back_to_circular(self) -> None:
        """A directed cycle (not a DAG) still renders all vertices."""
        g = Graph("cyc", directed=True)
        g.add_edges([("A", "B"), ("B", "C"), ("C", "A")])
        rendered = to_ascii(g)
        for vertex in ("A", "B", "C"):
            assert vertex in rendered

    def test_undirected_contains_every_vertex(self, triangle_graph: Graph) -> None:
        """An undirected graph renders every vertex via the circular layout."""
        rendered = to_ascii(triangle_graph)
        for vertex in triangle_graph.vertices():
            assert vertex in rendered

    def test_self_loop_does_not_crash(self) -> None:
        """A self-loop is skipped rather than raising during edge routing."""
        g = Graph("loop", directed=True)
        g.add_edge("A", "A")
        assert "A" in to_ascii(g)

    @pytest.mark.parametrize(
        "raw",
        [
            {"label": "D", "directed": True, "graph": {"A": ["B", "C"], "B": ["C"], "C": []}},
            {"label": "U", "graph": {"a": ["b", "c"], "b": ["a"], "c": ["a"]}},
        ],
    )
    def test_render_is_deterministic(self, raw: dict) -> None:
        """Rendering the same graph twice yields identical art."""
        g = Graph(input_graph=json.dumps(raw))
        assert to_ascii(g) == to_ascii(g)


class TestPublicSurface:
    """to_ascii is exposed at the package root (but not on Graph)."""

    def test_top_level_export(self, directed_dag: Graph) -> None:
        """to_ascii is importable directly from the package root."""
        import graphworks

        assert "to_ascii" in graphworks.__all__
        assert graphworks.to_ascii(directed_dag) == to_ascii(directed_dag)

    def test_not_a_graph_method(self) -> None:
        """to_ascii is intentionally not (yet) a Graph method."""
        assert not hasattr(Graph, "to_ascii")
