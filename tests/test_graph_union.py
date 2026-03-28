"""Unit tests for Graph union operators (``|`` and ``|=``).

Tests cover:
- ``__or__``: creates a new graph from the union of two graphs
- ``__ior__``: merges another graph into self in place
- Edge cases: empty graphs, overlapping vertices/edges, metadata precedence
- Error cases: directed/undirected mismatch, non-Graph operand
"""

from __future__ import annotations

import pytest

from graphworks.edge import Edge
from graphworks.graph import Graph

# ---------------------------------------------------------------------------
# __or__ — new graph from union
# ---------------------------------------------------------------------------


class TestGraphOr:
    """Tests for ``g1 | g2`` producing a new graph."""

    def test_disjoint_graphs(self) -> None:
        g1 = Graph("left")
        g1.add_edge("A", "B")
        g2 = Graph("right")
        g2.add_edge("C", "D")

        result = g1 | g2
        assert result.order == 4
        assert result.size == 2
        assert set(result.vertices()) == {"A", "B", "C", "D"}

    def test_overlapping_vertices(self) -> None:
        g1 = Graph("left")
        g1.add_edge("A", "B")
        g2 = Graph("right")
        g2.add_edge("B", "C")

        result = g1 | g2
        assert result.order == 3
        assert result.size == 2
        assert result.edge("A", "B") is not None
        assert result.edge("B", "C") is not None

    def test_overlapping_edges(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B", weight=1.0)
        g2 = Graph()
        g2.add_edge("A", "B", weight=99.0)

        result = g1 | g2
        assert result.size == 1
        e = result.edge("A", "B")
        assert e is not None
        assert e.weight == pytest.approx(99.0), "Right operand edge should win"

    def test_returns_new_graph(self) -> None:
        g1 = Graph("left")
        g1.add_edge("A", "B")
        g2 = Graph("right")
        g2.add_edge("C", "D")

        result = g1 | g2
        assert result is not g1
        assert result is not g2
        assert g1.order == 2, "Original should be unmodified"
        assert g2.order == 2, "Original should be unmodified"

    def test_label_combined(self) -> None:
        g1 = Graph("alpha")
        g2 = Graph("beta")
        assert (g1 | g2).label == "alpha | beta"

    def test_label_empty_both(self) -> None:
        assert (Graph() | Graph()).label == ""

    def test_label_one_empty(self) -> None:
        g1 = Graph("named")
        g2 = Graph()
        assert (g1 | g2).label == "named | "

    def test_directed_preserved(self) -> None:
        g1 = Graph(directed=True)
        g1.add_edge("A", "B")
        g2 = Graph(directed=True)
        g2.add_edge("B", "C")

        result = g1 | g2
        assert result.directed

    def test_weighted_either(self) -> None:
        g1 = Graph(weighted=True)
        g2 = Graph(weighted=False)
        assert (g1 | g2).weighted
        assert (g2 | g1).weighted

    def test_weighted_neither(self) -> None:
        assert not (Graph() | Graph()).weighted

    def test_directed_mismatch_raises(self) -> None:
        g1 = Graph(directed=True)
        g2 = Graph(directed=False)
        with pytest.raises(
            TypeError, match="unsupported operand type(s) for |: 'Graph' and 'Graph'"
        ):
            _ = g1 | g2

    def test_non_graph_returns_not_implemented(self) -> None:
        g = Graph()
        assert g.__or__("not a graph") is NotImplemented

    def test_empty_union_empty(self) -> None:
        result = Graph() | Graph()
        assert result.order == 0
        assert result.size == 0

    def test_empty_union_nonempty(self) -> None:
        g1 = Graph()
        g2 = Graph()
        g2.add_edge("A", "B")

        result = g1 | g2
        assert result.order == 2
        assert result.size == 1

    def test_nonempty_union_empty(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()

        result = g1 | g2
        assert result.order == 2
        assert result.size == 1

    def test_vertex_metadata_left_precedence(self) -> None:
        g1 = Graph()
        g1.add_vertex("hub", label="Left Label", attrs={"side": "left"})
        g2 = Graph()
        g2.add_vertex("hub", label="Right Label", attrs={"side": "right"})

        result = g1 | g2
        v = result.vertex("hub")
        assert v is not None
        assert v.label == "Left Label"
        assert v.attrs["side"] == "left"

    def test_edge_metadata_right_precedence(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B", label="old road")
        g2 = Graph()
        g2.add_edge("A", "B", label="new highway")

        result = g1 | g2
        e = result.edge("A", "B")
        assert e is not None
        assert e.label == "new highway"

    def test_preserves_edge_objects(self) -> None:
        g1 = Graph()
        custom_edge = Edge.create("X", "Y", weight=42.0, attrs={"toll": True})
        g1.add_edge(custom_edge)
        g2 = Graph()
        g2.add_vertex("Z")

        result = g1 | g2
        e = result.edge("X", "Y")
        assert e is not None
        assert e.weight == pytest.approx(42.0)
        assert e.attrs["toll"] is True

    def test_self_loops_preserved(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "A")
        g2 = Graph()

        result = g1 | g2
        e = result.edge("A", "A")
        assert e is not None

    def test_multiple_unions_chained(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("C", "D")
        g3 = Graph()
        g3.add_edge("E", "F")

        result = g1 | g2 | g3
        assert result.order == 6
        assert result.size == 3

    def test_directed_edges_not_reversed(self) -> None:
        g1 = Graph(directed=True)
        g1.add_edge("A", "B")
        g2 = Graph(directed=True)
        g2.add_edge("C", "D")

        result = g1 | g2
        assert result.edge("A", "B") is not None
        assert result.edge("B", "A") is None
        assert result.edge("C", "D") is not None
        assert result.edge("D", "C") is None

    def test_large_union(self) -> None:
        g1 = Graph()
        g1.add_edges([(f"L{i}", f"L{i + 1}") for i in range(50)])
        g2 = Graph()
        g2.add_edges([(f"R{i}", f"R{i + 1}") for i in range(50)])

        result = g1 | g2
        assert result.order == 102
        assert result.size == 100


# ---------------------------------------------------------------------------
# __ior__ — in-place merge
# ---------------------------------------------------------------------------


class TestGraphIor:
    """Tests for ``g1 |= g2`` merging into g1 in place."""

    def test_basic_merge(self) -> None:
        g1 = Graph("base")
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("C", "D")

        g1 |= g2
        assert g1.order == 4
        assert g1.size == 2

    def test_returns_self(self) -> None:
        g1 = Graph()
        g2 = Graph()
        g2.add_vertex("X")

        original_id = id(g1)
        g1 |= g2
        assert id(g1) == original_id

    def test_label_unchanged(self) -> None:
        g1 = Graph("original")
        g2 = Graph("other")

        g1 |= g2
        assert g1.label == "original"

    def test_overlapping_vertices_keeps_left(self) -> None:
        g1 = Graph()
        g1.add_vertex("hub", label="Original")
        g2 = Graph()
        g2.add_vertex("hub", label="Incoming")

        g1 |= g2
        v = g1.vertex("hub")
        assert v is not None
        assert v.label == "Original"

    def test_overlapping_edges_overwrites(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B", weight=1.0)
        g2 = Graph()
        g2.add_edge("A", "B", weight=99.0)

        g1 |= g2
        e = g1.edge("A", "B")
        assert e is not None
        assert e.weight == pytest.approx(99.0)

    def test_weighted_promotion(self) -> None:
        g1 = Graph()
        g2 = Graph(weighted=True)

        g1 |= g2
        assert g1.weighted

    def test_weighted_not_demoted(self) -> None:
        g1 = Graph(weighted=True)
        g2 = Graph()

        g1 |= g2
        assert g1.weighted

    def test_directed_mismatch_raises(self) -> None:
        g1 = Graph(directed=True)
        g2 = Graph(directed=False)
        with pytest.raises(
            TypeError, match="unsupported operand type(s) for |=: 'Graph' and 'Graph'"
        ):
            g1 |= g2

    def test_non_graph_returns_not_implemented(self) -> None:
        g = Graph()
        assert g.__ior__("not a graph") is NotImplemented

    def test_other_unchanged(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("C", "D")

        g1 |= g2
        assert g2.order == 2, "Right operand should be unmodified"
        assert "A" not in g2.vertices()

    def test_merge_empty_into_nonempty(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()

        g1 |= g2
        assert g1.order == 2
        assert g1.size == 1

    def test_merge_nonempty_into_empty(self) -> None:
        g1 = Graph()
        g2 = Graph()
        g2.add_edge("A", "B")

        g1 |= g2
        assert g1.order == 2
        assert g1.size == 1

    def test_chained_ior(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("C", "D")
        g3 = Graph()
        g3.add_edge("E", "F")

        g1 |= g2
        g1 |= g3
        assert g1.order == 6
        assert g1.size == 3


# ---------------------------------------------------------------------------
# Integration: union with other API features
# ---------------------------------------------------------------------------


class TestUnionIntegration:
    """Integration tests combining union with other Graph features."""

    def test_union_then_algorithm(self) -> None:
        """Union result works with algorithm functions."""
        from graphworks.algorithms.properties import is_connected

        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("B", "C")

        result = g1 | g2
        assert is_connected(result)

    def test_union_then_fluent_chain(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("C", "D")

        result = g1 | g2
        result.add_edge("B", "C").add_vertex("E")
        assert result.order == 5
        assert result.size == 3

    def test_ior_then_fluent_chain(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("C", "D")

        g1 |= g2
        g1.add_edge("B", "C")
        assert g1.order == 4
        assert g1.size == 3

    def test_union_preserves_vertex_objects_from_add_vertex_kwargs(self) -> None:
        g1 = Graph()
        g1.add_vertex("hub", label="Central", attrs={"rank": 1})
        g1.add_edge("hub", "A")

        g2 = Graph()
        g2.add_edge("hub", "B")

        result = g1 | g2
        v = result.vertex("hub")
        assert v is not None
        assert v.label == "Central"
        assert v.attrs["rank"] == 1

    def test_union_with_batch_edges(self) -> None:
        g1 = Graph()
        g1.add_edges([("A", "B"), ("B", "C")])
        g2 = Graph()
        g2.add_edges([("C", "D"), ("D", "E")])

        result = g1 | g2
        assert result.order == 5
        assert result.size == 4

    def test_union_adjacency_matrix(self) -> None:
        g1 = Graph()
        g1.add_edge("A", "B")
        g2 = Graph()
        g2.add_edge("B", "C")

        result = g1 | g2
        matrix = result.adjacency_matrix()
        assert len(matrix) == 3
        assert all(len(row) == 3 for row in matrix)
