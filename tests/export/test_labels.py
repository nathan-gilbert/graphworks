"""Unit tests for :mod:`graphworks.export._labels`."""

from __future__ import annotations

from graphworks.export._labels import RenderStyle, edge_annotation, vertex_text
from graphworks.graph import Graph


class TestVertexText:
    """Resolving a vertex's display text."""

    def test_label_preferred_when_set(self) -> None:
        """A set label wins over the name."""
        g = Graph(directed=True)
        g.add_vertex("A", label="Start")
        assert vertex_text(g, "A") == "Start"

    def test_falls_back_to_name(self) -> None:
        """Without a label, the name is used."""
        g = Graph(directed=True)
        g.add_vertex("A")
        assert vertex_text(g, "A") == "A"

    def test_use_label_false_forces_name(self) -> None:
        """use_label=False returns the name even when a label exists."""
        g = Graph(directed=True)
        g.add_vertex("A", label="Start")
        assert vertex_text(g, "A", use_label=False) == "A"

    def test_missing_vertex_returns_name(self) -> None:
        """An unknown vertex name is returned verbatim."""
        assert vertex_text(Graph(), "ghost") == "ghost"


class TestEdgeAnnotation:
    """Resolving an edge's annotation content."""

    def test_no_source_is_empty(self) -> None:
        """A root (no source) has no annotation."""
        assert edge_annotation(Graph(), None, "A", style=RenderStyle()) == ""

    def test_missing_edge_is_empty(self) -> None:
        """A non-existent edge has no annotation."""
        g = Graph(directed=True)
        g.add_vertex("A")
        g.add_vertex("B")
        assert edge_annotation(g, "A", "B", style=RenderStyle()) == ""

    def test_label_only(self) -> None:
        """An unweighted edge shows just its label."""
        g = Graph(directed=True)
        g.add_edge("A", "B", label="retry")
        assert edge_annotation(g, "A", "B", style=RenderStyle()) == "retry"

    def test_label_and_weight(self) -> None:
        """A weighted, labeled edge combines both, comma-separated."""
        g = Graph(directed=True, weighted=True)
        g.add_edge("A", "B", label="retry", weight=3)
        assert edge_annotation(g, "A", "B", style=RenderStyle()) == "retry, w=3"

    def test_weights_none_follows_graph_flag(self) -> None:
        """weights=None hides the weight on a graph not declared weighted."""
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=3)
        assert edge_annotation(g, "A", "B", style=RenderStyle()) == ""

    def test_weights_forced_true(self) -> None:
        """weights=True shows the weight regardless of the graph flag."""
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=3)
        style = RenderStyle(weights=True)
        assert edge_annotation(g, "A", "B", style=style) == "w=3"

    def test_edge_labels_disabled(self) -> None:
        """edge_labels=False drops the label but keeps the weight."""
        g = Graph(directed=True, weighted=True)
        g.add_edge("A", "B", label="retry", weight=3)
        style = RenderStyle(edge_labels=False)
        assert edge_annotation(g, "A", "B", style=style) == "w=3"
