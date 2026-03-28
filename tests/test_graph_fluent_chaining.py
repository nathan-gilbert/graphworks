"""Unit tests for the Graph fluent API enhancements.

Tests cover:
1. Fluent chaining — ``add_vertex`` and ``add_edge`` return ``self``
2. Batch ``add_edges`` — accepts iterables of edge specifications
3. ``add_vertex`` with kwargs — forwards ``label`` and ``attrs`` to ``Vertex.create``
4. ``add_edge`` accepts ``Edge`` objects — pre-built edges as first positional arg
"""

from __future__ import annotations

import pytest

from graphworks.edge import Edge
from graphworks.graph import Graph
from graphworks.vertex import Vertex

# ---------------------------------------------------------------------------
# 1. Fluent chaining
# ---------------------------------------------------------------------------


class TestFluentChaining:
    """Verify that ``add_vertex`` and ``add_edge`` return ``self``."""

    def test_add_vertex_returns_self(self) -> None:
        g = Graph()
        result = g.add_vertex("A")
        assert result is g

    def test_add_edge_returns_self(self) -> None:
        g = Graph()
        result = g.add_edge("A", "B")
        assert result is g

    def test_add_edges_returns_self(self) -> None:
        g = Graph()
        result = g.add_edges([("A", "B")])
        assert result is g

    def test_chain_add_vertex(self) -> None:
        g = Graph()
        g.add_vertex("A").add_vertex("B").add_vertex("C")
        assert sorted(g.vertices()) == ["A", "B", "C"]

    def test_chain_add_edge(self) -> None:
        g = Graph("triangle")
        g.add_edge("A", "B").add_edge("B", "C").add_edge("C", "A")
        assert g.order == 3
        assert g.size == 3

    def test_chain_mixed(self) -> None:
        g = Graph()
        g.add_vertex("X", label="Entry").add_edge("X", "Y").add_vertex("Z")
        assert g.order == 3
        assert g.size == 1
        v = g.vertex("X")
        assert v is not None
        assert v.label == "Entry"

    def test_chain_add_edges_then_vertex(self) -> None:
        g = Graph()
        g.add_edges([("A", "B"), ("B", "C")]).add_vertex("D")
        assert g.order == 4
        assert g.size == 2


# ---------------------------------------------------------------------------
# 2. Batch add_edges
# ---------------------------------------------------------------------------


class TestAddEdges:
    """Verify batch edge insertion via ``add_edges``."""

    def test_tuple_pairs(self) -> None:
        g = Graph()
        g.add_edges([("A", "B"), ("B", "C"), ("C", "D")])
        assert g.order == 4
        assert g.size == 3

    def test_tuple_with_attrs(self) -> None:
        g = Graph()
        g.add_edges(
            [
                ("A", "B", {"weight": 3.5, "label": "highway"}),
                ("B", "C", {"weight": 2.0}),
            ]
        )
        e_ab = g.edge("A", "B")
        assert e_ab is not None
        assert e_ab.weight == pytest.approx(3.5)
        assert e_ab.label == "highway"

        e_bc = g.edge("B", "C")
        assert e_bc is not None
        assert e_bc.weight == pytest.approx(2.0)
        assert e_bc.label is None

    def test_edge_objects(self) -> None:
        g = Graph()
        edges = [
            Edge.create("X", "Y", weight=1.0),
            Edge.create("Y", "Z", label="bridge"),
        ]
        g.add_edges(edges)
        assert g.order == 3
        assert g.size == 2
        assert g.edge("X", "Y") is not None
        assert g.edge("Y", "Z") is not None

    def test_mixed_specs(self) -> None:
        g = Graph()
        g.add_edges(
            [
                ("A", "B"),
                ("B", "C", {"weight": 5.0}),
                Edge.create("C", "D", directed=True, label="arc"),
            ]
        )
        assert g.order == 4
        assert g.size == 3

    def test_empty_iterable(self) -> None:
        g = Graph()
        g.add_edges([])
        assert g.order == 0
        assert g.size == 0

    def test_generator_input(self) -> None:
        def pairs():
            yield ("A", "B")
            yield ("B", "C")

        g = Graph()
        g.add_edges(pairs())
        assert g.size == 2

    def test_auto_creates_vertices(self) -> None:
        g = Graph()
        g.add_edges([("X", "Y"), ("Y", "Z")])
        assert set(g.vertices()) == {"X", "Y", "Z"}

    def test_invalid_tuple_length_raises(self) -> None:
        g = Graph()
        with pytest.raises(TypeError, match="2 or 3 elements"):
            g.add_edges([("A",)])  # type: ignore[list-item]

    def test_invalid_tuple_four_elements_raises(self) -> None:
        g = Graph()
        with pytest.raises(TypeError, match="2 or 3 elements"):
            g.add_edges([("A", "B", {}, "extra")])  # type: ignore[list-item]

    def test_non_dict_third_element_raises(self) -> None:
        g = Graph()
        with pytest.raises(TypeError, match="must be a dict"):
            g.add_edges([("A", "B", 42)])  # type: ignore[list-item]

    def test_non_tuple_non_edge_raises(self) -> None:
        g = Graph()
        with pytest.raises(TypeError, match="Expected a tuple or Edge"):
            g.add_edges(["not_valid"])  # type: ignore[list-item]

    def test_attrs_dict_weight_only(self) -> None:
        g = Graph()
        g.add_edges([("A", "B", {"weight": 7.0})])
        e = g.edge("A", "B")
        assert e is not None
        assert e.weight == pytest.approx(7.0)
        assert e.label is None

    def test_attrs_dict_label_only(self) -> None:
        g = Graph()
        g.add_edges([("A", "B", {"label": "road"})])
        e = g.edge("A", "B")
        assert e is not None
        assert e.weight is None
        assert e.label == "road"

    def test_attrs_dict_empty(self) -> None:
        g = Graph()
        g.add_edges([("A", "B", {})])
        e = g.edge("A", "B")
        assert e is not None
        assert e.weight is None
        assert e.label is None


# ---------------------------------------------------------------------------
# 3. add_vertex with kwargs
# ---------------------------------------------------------------------------


class TestAddVertexKwargs:
    """Verify ``add_vertex`` forwards ``label`` and ``attrs`` to ``Vertex.create``."""

    def test_label_kwarg(self) -> None:
        g = Graph()
        g.add_vertex("hub", label="Central")
        v = g.vertex("hub")
        assert v is not None
        assert v.label == "Central"
        assert v.display_name == "Central"

    def test_attrs_kwarg(self) -> None:
        g = Graph()
        g.add_vertex("hub", attrs={"rank": 1, "color": "red"})
        v = g.vertex("hub")
        assert v is not None
        assert v.attrs["rank"] == 1
        assert v.attrs["color"] == "red"

    def test_label_and_attrs(self) -> None:
        g = Graph()
        g.add_vertex("n1", label="Start", attrs={"priority": "high"})
        v = g.vertex("n1")
        assert v is not None
        assert v.label == "Start"
        assert v.attrs["priority"] == "high"

    def test_attrs_frozen(self) -> None:
        raw = {"key": "original"}
        g = Graph()
        g.add_vertex("n1", attrs=raw)
        raw["key"] = "mutated"
        v = g.vertex("n1")
        assert v is not None
        assert v.attrs["key"] == "original"

    def test_vertex_object_ignores_kwargs(self) -> None:
        v = Vertex.create("obj", label="Original")
        g = Graph()
        g.add_vertex(v, label="Ignored", attrs={"ignored": True})
        result = g.vertex("obj")
        assert result is not None
        assert result.label == "Original"
        assert result.attrs == {}

    def test_no_kwargs_plain_string(self) -> None:
        g = Graph()
        g.add_vertex("plain")
        v = g.vertex("plain")
        assert v is not None
        assert v.label is None
        assert v.attrs == {}

    def test_duplicate_vertex_idempotent_with_kwargs(self) -> None:
        g = Graph()
        g.add_vertex("A", label="First")
        g.add_vertex("A", label="Second")
        v = g.vertex("A")
        assert v is not None
        assert v.label == "First"
        assert g.order == 1

    def test_chained_with_kwargs(self) -> None:
        g = Graph()
        g.add_vertex("A", label="Start").add_vertex("B", label="End")
        assert g.vertex("A").label == "Start"  # type: ignore[union-attr]
        assert g.vertex("B").label == "End"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# 4. add_edge accepts Edge objects
# ---------------------------------------------------------------------------


class TestAddEdgeObject:
    """Verify ``add_edge`` accepts pre-built :class:`Edge` objects."""

    def test_basic_edge_object(self) -> None:
        g = Graph()
        e = Edge("A", "B")
        g.add_edge(e)
        assert g.order == 2
        assert g.size == 1

    def test_edge_create_factory(self) -> None:
        g = Graph()
        e = Edge.create("X", "Y", weight=3.14, label="bridge")
        g.add_edge(e)
        found = g.edge("X", "Y")
        assert found is not None
        assert found.weight == pytest.approx(3.14)
        assert found.label == "bridge"

    def test_edge_object_preserves_directed(self) -> None:
        g = Graph()
        e = Edge("A", "B", directed=True)
        g.add_edge(e)
        found = g.edge("A", "B")
        assert found is not None
        assert found.directed

    def test_edge_object_preserves_attrs(self) -> None:
        g = Graph()
        e = Edge.create("A", "B", attrs={"color": "red"})
        g.add_edge(e)
        found = g.edge("A", "B")
        assert found is not None
        assert found.attrs["color"] == "red"

    def test_edge_object_auto_creates_vertices(self) -> None:
        g = Graph()
        g.add_edge(Edge("P", "Q"))
        assert set(g.vertices()) == {"P", "Q"}

    def test_edge_object_ignores_kwargs(self) -> None:
        g = Graph()
        e = Edge.create("A", "B", weight=10.0)
        g.add_edge(e, weight=99.0, label="ignored")
        found = g.edge("A", "B")
        assert found is not None
        assert found.weight == pytest.approx(10.0)
        assert found.label is None

    def test_edge_object_chained(self) -> None:
        g = Graph()
        e1 = Edge("A", "B")
        e2 = Edge("B", "C")
        g.add_edge(e1).add_edge(e2)
        assert g.size == 2

    def test_str_source_missing_target_raises(self) -> None:
        g = Graph()
        with pytest.raises(TypeError, match="target is required"):
            g.add_edge("A")  # type: ignore[call-overload]

    def test_edge_object_target_param_ignored(self) -> None:
        g = Graph()
        e = Edge("A", "B")
        g.add_edge(e, "IGNORED")
        assert g.edge("A", "B") is not None
        assert "IGNORED" not in g.vertices()


# ---------------------------------------------------------------------------
# Integration: combining all enhancements
# ---------------------------------------------------------------------------


class TestFluentAPIIntegration:
    """Integration tests exercising multiple enhancements together."""

    def test_full_construction_pipeline(self) -> None:
        g = Graph("network")
        g.add_vertex("hub", label="Central", attrs={"rank": 1}).add_edges(
            [
                ("hub", "A"),
                ("hub", "B", {"weight": 2.5}),
                Edge.create("hub", "C", label="express"),
            ]
        ).add_vertex("D").add_edge("C", "D")

        assert g.order == 5
        assert g.size == 4

        v = g.vertex("hub")
        assert v is not None
        assert v.label == "Central"
        assert v.attrs["rank"] == 1

        e = g.edge("hub", "B")
        assert e is not None
        assert e.weight == pytest.approx(2.5)

        e_express = g.edge("hub", "C")
        assert e_express is not None
        assert e_express.label == "express"

    def test_directed_graph_chaining(self) -> None:
        g = Graph("dag", directed=True)
        g.add_edges(
            [
                ("compile", "lint"),
                ("compile", "typecheck"),
                ("test", "compile"),
                ("package", "test"),
            ]
        )
        assert g.order == 5
        assert g.size == 4
        assert g.edge("compile", "lint") is not None
        assert g.edge("lint", "compile") is None

    def test_weighted_graph_batch(self) -> None:
        g = Graph("routes", weighted=True)
        g.add_edges(
            [
                ("Denver", "SLC", {"weight": 525.0, "label": "I-70/I-15"}),
                ("SLC", "Boise", {"weight": 340.0, "label": "I-84"}),
                ("Boise", "Portland", {"weight": 430.0, "label": "I-84"}),
            ]
        )
        assert g.order == 4
        assert g.size == 3

        e = g.edge("Denver", "SLC")
        assert e is not None
        assert e.weight == pytest.approx(525.0)
        assert e.label == "I-70/I-15"

    def test_existing_tests_still_pass_pattern(self, simple_edge_json) -> None:
        """Ensure the old string-based ``add_edge`` API still works identically."""
        g = Graph()
        g.add_edge("A", "B")
        assert g.size == 1
        assert g.order == 2
        assert g.edge("A", "B") is not None

    def test_existing_vertex_object_pattern(self) -> None:
        """Ensure the old Vertex-object ``add_vertex`` API still works identically."""
        g = Graph()
        g.add_vertex(Vertex.create("hub", label="Central", attrs={"rank": 1}))
        v = g.vertex("hub")
        assert v is not None
        assert v.label == "Central"
