"""Unit tests for :mod:`graphworks.export.text_utils`."""

from __future__ import annotations

import json

import pytest

from graphworks.export.text_utils import to_text
from graphworks.graph import Graph


class TestToText:
    """Tests for to_text."""

    def test_empty_graph(self) -> None:
        """An empty graph renders the root token and an explicit marker."""
        assert to_text(Graph("empty")) == "empty\n(empty graph)"

    def test_unlabeled_graph_uses_placeholder_root(self) -> None:
        """An unlabeled graph falls back to the literal 'graph' root token."""
        g = Graph()
        g.add_edge("A", "B")
        assert to_text(g).splitlines()[0] == "graph"

    def test_label_is_root_line(self, simple_edge_graph: Graph) -> None:
        """The graph label is the first (root) line of the output."""
        assert to_text(simple_edge_graph).splitlines()[0] == "my graph"

    def test_simple_tree(self) -> None:
        """A small tree renders with the expected connectors."""
        g = Graph("demo")
        g.add_edge("A", "B").add_edge("A", "C").add_edge("B", "D")
        assert to_text(g) == ("demo\n" "└── A\n" "    ├── B\n" "    │   └── D\n" "    └── C")

    def test_every_vertex_appears(self, connected_graph: Graph) -> None:
        """Each vertex name appears at least once in the rendering."""
        rendered = to_text(connected_graph)
        for vertex in connected_graph.vertices():
            assert vertex in rendered

    def test_isolated_vertices_are_roots(self, isolated_graph: Graph) -> None:
        """Vertices with no edges render as sibling leaves under the root."""
        assert to_text(isolated_graph) == "graph\n├── a\n├── b\n└── c"

    def test_directed_sources_render_first(self, directed_dag: Graph) -> None:
        """In a DAG, in-degree-zero vertices seed the forest before others."""
        body = to_text(directed_dag).splitlines()[1:]
        first_roots = [line for line in body if line[0] in "├└"]
        # E and F are the only sources in directed_dag_json.
        assert first_roots[0].endswith(("E", "F"))

    def test_cycle_terminates_with_marker(self, directed_cycle_graph: Graph) -> None:
        """A directed cycle is broken with a trailing '...' rather than recursing forever."""
        rendered = to_text(directed_cycle_graph)
        assert "..." in rendered
        # The back-edge A -> ... -> A closes onto the already-shown A.
        assert "A ..." in rendered

    def test_undirected_parent_edge_suppressed(self) -> None:
        """A child does not redundantly list the parent it was reached from."""
        g = Graph("pair")
        g.add_edge("a", "b").add_edge("b", "a")  # both directions declared
        # 'a' is root -> 'b'; 'b' must not re-list 'a' as a child.
        assert to_text(g) == "pair\n└── a\n    └── b"

    def test_seen_marker_for_shared_child(self) -> None:
        """A vertex reachable two ways is fully drawn once and marked on reuse."""
        g = Graph("diamond", directed=True)
        g.add_edges([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
        rendered = to_text(g)
        assert rendered.count("└── D") + rendered.count("├── D") >= 1
        assert "D ..." in rendered

    def test_weighted_edges_annotated(self) -> None:
        """Edge weights are shown when the graph is weighted."""
        g = Graph("weighted", weighted=True)
        g.add_edge("A", "B", weight=3).add_edge("B", "C", weight=1.5)
        assert to_text(g) == "weighted\n└── A\n    └── B [w=3]\n        └── C [w=1.5]"

    def test_unweighted_graph_has_no_annotation(self, simple_edge_graph: Graph) -> None:
        """Unweighted graphs carry no weight annotation."""
        assert "w=" not in to_text(simple_edge_graph)

    def test_weighted_graph_edge_without_weight_unannotated(self) -> None:
        """A weighted graph still omits the annotation for edges that carry no weight."""
        g = Graph("weighted", weighted=True)
        g.add_edge("A", "B")  # no weight supplied
        assert to_text(g) == "weighted\n└── A\n    └── B"

    def test_vertex_label_shown_by_default(self) -> None:
        """A vertex's label replaces its name in the output when set."""
        g = Graph("g", directed=True)
        g.add_vertex("A", label="Start")
        g.add_edge("A", "B")
        assert to_text(g) == "g\n└── Start\n    └── B"

    def test_vertex_labels_can_be_disabled(self) -> None:
        """vertex_labels=False renders the name even when a label is set."""
        g = Graph("g", directed=True)
        g.add_vertex("A", label="Start")
        g.add_edge("A", "B")
        assert to_text(g, vertex_labels=False) == "g\n└── A\n    └── B"

    def test_edge_label_shown_by_default(self) -> None:
        """An edge's label is annotated in brackets."""
        g = Graph("g", directed=True)
        g.add_edge("A", "B", label="retry")
        assert to_text(g) == "g\n└── A\n    └── B [retry]"

    def test_edge_label_and_weight_combined(self) -> None:
        """Label and weight share a single bracketed annotation."""
        g = Graph("g", directed=True, weighted=True)
        g.add_edge("A", "B", label="retry", weight=3)
        assert to_text(g) == "g\n└── A\n    └── B [retry, w=3]"

    def test_edge_labels_can_be_disabled(self) -> None:
        """edge_labels=False hides labels but leaves weights intact."""
        g = Graph("g", directed=True, weighted=True)
        g.add_edge("A", "B", label="retry", weight=3)
        assert to_text(g, edge_labels=False) == "g\n└── A\n    └── B [w=3]"

    def test_weights_forced_on_unweighted_graph(self) -> None:
        """weights=True shows weights even when the graph is not declared weighted."""
        g = Graph("g", directed=True)
        g.add_edge("A", "B", weight=3)
        assert to_text(g, weights=True) == "g\n└── A\n    └── B [w=3]"

    def test_self_loop_marked(self) -> None:
        """A self-loop renders the vertex as a seen leaf beneath itself."""
        g = Graph("loop", directed=True)
        g.add_edge("A", "A")
        assert to_text(g) == "loop\n└── A\n    └── A ..."

    @pytest.mark.parametrize(
        "raw",
        [
            {"label": "L", "graph": {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}},
            {"label": "C", "directed": True, "graph": {"A": ["B"], "B": ["A"]}},
            {"label": "K", "graph": {"a": ["b", "c"], "b": ["a", "c"], "c": ["a", "b"]}},
        ],
    )
    def test_output_is_deterministic(self, raw: dict) -> None:
        """Rendering the same graph twice yields identical output."""
        g = Graph(input_graph=json.dumps(raw))
        assert to_text(g) == to_text(g)


class TestPublicSurface:
    """to_text is exposed at the package root and in graphworks.export."""

    def test_not_a_graph_method(self) -> None:
        """Rendering is a free function, like every other algorithm and exporter."""
        assert not hasattr(Graph, "to_text")

    def test_top_level_export(self, simple_edge_graph: Graph) -> None:
        """to_text is importable directly from the package root."""
        import graphworks

        assert "to_text" in graphworks.__all__
        assert graphworks.to_text(simple_edge_graph) == to_text(simple_edge_graph)

    def test_export_package(self, simple_edge_graph: Graph) -> None:
        """to_text is importable from graphworks.export."""
        from graphworks import export

        assert export.to_text(simple_edge_graph) == to_text(simple_edge_graph)
