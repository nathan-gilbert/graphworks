"""Unit tests for :mod:`graphworks.algorithms.properties`."""

from __future__ import annotations

import json

import pytest

from graphworks.algorithms.properties import (
    complement,
    degree_sequence,
    density,
    diameter,
    is_complete,
    is_connected,
    is_degree_sequence,
    is_dense,
    is_erdos_gallai,
    is_regular,
    is_simple,
    is_sparse,
    max_degree,
    min_degree,
    vertex_degree,
)
from graphworks.graph import Graph

# ---------------------------------------------------------------------------
# Degree helpers
# ---------------------------------------------------------------------------


class TestVertexDegree:
    def test_without_self_loop(self) -> None:
        data = {"graph": {"a": ["b", "c"], "b": ["a"], "c": ["a"]}}
        assert vertex_degree(Graph(input_graph=json.dumps(data)), "b") == 1

    def test_self_loop_counts_twice(self) -> None:
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        assert vertex_degree(Graph(input_graph=json.dumps(data)), "a") == 4

    def test_isolated_zero(self, isolated_graph) -> None:
        assert vertex_degree(isolated_graph, "a") == 0

    def test_multiple_neighbours(self, big_graph) -> None:
        assert vertex_degree(big_graph, "c") == 4

    def test_undirected_counts_both_endpoints(self) -> None:
        g = Graph().add_edge("A", "B").add_edge("B", "C")
        assert [vertex_degree(g, v) for v in "ABC"] == [1, 2, 1]

    def test_directed_is_in_plus_out(self) -> None:
        g = Graph(directed=True).add_edge("A", "B").add_edge("C", "B").add_edge("B", "D")
        assert vertex_degree(g, "B") == 3

    def test_missing_vertex(self, big_graph) -> None:
        with pytest.raises(KeyError):
            vertex_degree(big_graph, "zz")


class TestMinMaxDegree:
    def test_min(self) -> None:
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        assert min_degree(Graph(input_graph=json.dumps(data))) == 1

    def test_max(self) -> None:
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        assert max_degree(Graph(input_graph=json.dumps(data))) == 4

    def test_equal_for_regular(self, isolated_graph) -> None:
        assert min_degree(isolated_graph) == max_degree(isolated_graph)

    @pytest.mark.parametrize("func", [min_degree, max_degree])
    def test_empty_graph_raises(self, func) -> None:
        with pytest.raises(ValueError, match="no vertices"):
            func(Graph())


class TestDegreeSequence:
    def test_sorted_descending(self) -> None:
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        assert degree_sequence(Graph(input_graph=json.dumps(data))) == [4, 1, 1]

    def test_all_zeros(self, isolated_graph) -> None:
        assert all(d == 0 for d in degree_sequence(isolated_graph))


# ---------------------------------------------------------------------------
# Sequence predicates
# ---------------------------------------------------------------------------


class TestIsDegreeSequence:
    @pytest.mark.parametrize(
        ("seq", "expected"),
        [
            ([], True),
            ([2, 2], True),
            ([4, 2, 2], True),
            ([1, 2, 3], False),
            ([3, 1, 1], False),
            ([1], False),
            ([0, 0, 0], True),
            ([2, 0, -2], False),
        ],
    )
    def test_various(self, seq, expected) -> None:
        assert is_degree_sequence(seq) is expected


class TestIsErdosGallai:
    @pytest.mark.parametrize(
        ("seq", "expected"),
        [
            ([], True),
            ([1], False),
            ([2, 2, 4], False),
            ([32, 8, 4, 2, 2], False),
            ([6, 6, 6, 6, 5, 5, 2, 2], True),
            ([0, 0, 0], True),
            ([1, 1], True),
        ],
    )
    def test_various(self, seq, expected) -> None:
        assert is_erdos_gallai(seq) is expected


# ---------------------------------------------------------------------------
# Structural predicates
# ---------------------------------------------------------------------------


class TestIsRegular:
    def test_isolated_is_regular(self, isolated_graph) -> None:
        assert is_regular(isolated_graph)

    def test_triangle_is_regular(self, triangle_graph) -> None:
        assert is_regular(triangle_graph)

    def test_irregular(self, big_graph) -> None:
        assert not is_regular(big_graph)

    def test_built_triangle_is_regular(self) -> None:
        g = Graph().add_edges([("A", "B"), ("B", "C"), ("C", "A")])
        assert is_regular(g)
        assert degree_sequence(g) == [2, 2, 2]

    def test_path_is_not_regular(self) -> None:
        assert not is_regular(Graph().add_edge("A", "B").add_edge("B", "C"))


class TestIsSimple:
    def test_straight_line(self, straight_line_json) -> None:
        assert is_simple(Graph(input_graph=json.dumps(straight_line_json)))

    def test_lollipop(self, lollipop_json) -> None:
        assert is_simple(Graph(input_graph=json.dumps(lollipop_json)))

    def test_self_loop(self, self_loop_json) -> None:
        assert not is_simple(Graph(input_graph=json.dumps(self_loop_json)))

    def test_connected_with_self_loops(self, connected_json) -> None:
        assert not is_simple(Graph(input_graph=json.dumps(connected_json)))


class TestIsConnected:
    def test_connected(self, connected_graph) -> None:
        assert is_connected(connected_graph)

    def test_isolated_not_connected(self, isolated_graph) -> None:
        assert not is_connected(isolated_graph)

    def test_big_graph(self, big_graph) -> None:
        assert is_connected(big_graph)

    def test_empty_is_connected(self) -> None:
        assert is_connected(Graph())

    def test_directed_weakly_connected(self) -> None:
        assert is_connected(Graph(directed=True).add_edge("B", "A").add_edge("C", "A"))

    def test_directed_disconnected(self, disjoint_directed_graph) -> None:
        assert not is_connected(disjoint_directed_graph)


class TestIsComplete:
    def test_triangle(self, triangle_graph) -> None:
        assert is_complete(triangle_graph)

    def test_isolated_not_complete(self, isolated_graph) -> None:
        assert not is_complete(isolated_graph)

    def test_single_edge_is_k2(self, simple_edge_graph) -> None:
        assert is_complete(simple_edge_graph)

    def test_partial(self, straight_line_json) -> None:
        assert not is_complete(Graph(input_graph=json.dumps(straight_line_json)))

    def test_complete_directed(self) -> None:
        data = {"directed": True, "graph": {"a": ["b"], "b": ["a"]}}
        assert is_complete(Graph(input_graph=json.dumps(data)))

    def test_incomplete_directed(self) -> None:
        data = {"directed": True, "graph": {"A": ["B"], "B": []}}
        assert not is_complete(Graph(input_graph=json.dumps(data)))

    def test_built_triangle_complete(self) -> None:
        assert is_complete(Graph().add_edges([("A", "B"), ("B", "C"), ("C", "A")]))

    def test_self_loop_not_complete(self) -> None:
        assert not is_complete(Graph().add_edge("A", "B").add_edge("A", "A"))


class TestSparseAndDense:
    def test_isolated_sparse(self, isolated_graph) -> None:
        assert is_sparse(isolated_graph)

    def test_triangle_dense(self, triangle_graph) -> None:
        assert is_dense(triangle_graph)

    def test_sparse_not_dense(self, isolated_graph) -> None:
        assert not is_dense(isolated_graph)

    def test_complete_graph_not_sparse(self) -> None:
        k4 = Graph().add_edges([(a, b) for a in "ABCD" for b in "ABCD" if a < b])
        assert not is_sparse(k4)

    @pytest.mark.parametrize("fixture", ["isolated_graph", "triangle_graph", "big_graph"])
    def test_sparse_is_not_dense(self, fixture, request) -> None:
        g = request.getfixturevalue(fixture)
        assert is_sparse(g) is not is_dense(g)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class TestDensity:
    def test_connected(self, connected_graph) -> None:
        assert density(connected_graph) == pytest.approx(5 / 15)  # self-loops excluded

    def test_complete(self, triangle_graph) -> None:
        assert density(triangle_graph) == pytest.approx(1.0)

    def test_isolated_zero(self, isolated_graph) -> None:
        assert density(isolated_graph) == pytest.approx(0.0)

    def test_single_vertex_zero(self) -> None:
        g = Graph()
        g.add_vertex("A")
        assert density(g) == pytest.approx(0.0)

    def test_complete_directed_is_one(self) -> None:
        g = Graph(directed=True).add_edges([("A", "B"), ("B", "A")])
        assert density(g) == pytest.approx(1.0)

    def test_half_directed(self) -> None:
        assert density(Graph(directed=True).add_edge("A", "B")) == pytest.approx(0.5)


class TestDiameter:
    def test_big_graph(self, big_graph) -> None:
        assert diameter(big_graph) == 3

    def test_single_edge(self, simple_edge_graph) -> None:
        assert diameter(simple_edge_graph) == 1

    def test_disconnected_raises(self, isolated_graph) -> None:
        with pytest.raises(ValueError, match="infinite"):
            diameter(isolated_graph)

    def test_directed_not_strongly_connected_raises(self) -> None:
        with pytest.raises(ValueError, match="infinite"):
            diameter(Graph(directed=True).add_edge("A", "B"))

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="no vertices"):
            diameter(Graph())

    def test_single_vertex(self) -> None:
        assert diameter(Graph().add_vertex("A")) == 0

    def test_directed_cycle(self, circuit_graph) -> None:
        assert diameter(circuit_graph) == 2


# ---------------------------------------------------------------------------
# Derived graphs
# ---------------------------------------------------------------------------


class TestComplement:
    def test_label(self, isolated_graph) -> None:
        assert complement(isolated_graph).label == "complement"
        assert complement(Graph("g")).label == "g complement"

    def test_preserves_vertex_names(self, big_graph) -> None:
        assert complement(big_graph).vertices() == big_graph.vertices()

    def test_preserves_vertex_objects(self) -> None:
        g = Graph().add_vertex("A", label="Alpha")
        vertex = complement(g).vertex("A")
        assert vertex is not None
        assert vertex.label == "Alpha"

    def test_isolated_becomes_complete(self, isolated_graph) -> None:
        c = complement(isolated_graph)
        assert c.size == 3
        assert is_complete(c)

    def test_complete_becomes_empty(self, triangle_graph) -> None:
        assert complement(triangle_graph).size == 0

    def test_no_self_loops(self, isolated_graph) -> None:
        assert is_simple(complement(isolated_graph))

    def test_directed_preserved(self) -> None:
        c = complement(Graph(directed=True).add_edge("A", "B"))
        assert c.directed
        assert [(e.source, e.target) for e in c.edges()] == [("B", "A")]

    def test_double_complement_is_identity(self, big_graph) -> None:
        assert complement(complement(big_graph)) == big_graph
