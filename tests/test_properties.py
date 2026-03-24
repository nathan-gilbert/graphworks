"""Unit tests for :mod:`graphworks.algorithms.properties`."""

from __future__ import annotations

import json

import pytest

from graphworks.algorithms.properties import (
    degree_sequence,
    density,
    diameter,
    get_complement,
    invert,
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


class TestMinMaxDegree:
    def test_min(self) -> None:
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        assert min_degree(Graph(input_graph=json.dumps(data))) == 1

    def test_max(self) -> None:
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        assert max_degree(Graph(input_graph=json.dumps(data))) == 4

    def test_equal_for_regular(self, isolated_graph) -> None:
        assert min_degree(isolated_graph) == max_degree(isolated_graph)


class TestDegreeSequence:
    def test_sorted_descending(self) -> None:
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        assert degree_sequence(Graph(input_graph=json.dumps(data))) == (4, 1, 1)

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


class TestIsComplete:
    def test_triangle(self, triangle_graph) -> None:
        assert is_complete(triangle_graph)

    def test_isolated_not_complete(self, isolated_graph) -> None:
        assert not is_complete(isolated_graph)

    def test_partial(self, simple_edge_graph) -> None:
        assert not is_complete(simple_edge_graph)

    def test_complete_directed(self) -> None:
        data = {"directed": True, "graph": {"a": ["b"], "b": ["a"]}}
        assert is_complete(Graph(input_graph=json.dumps(data)))

    def test_incomplete_directed(self) -> None:
        data = {"directed": True, "graph": {"A": ["B"], "B": []}}
        assert not is_complete(Graph(input_graph=json.dumps(data)))


class TestSparseAndDense:
    def test_isolated_sparse(self, isolated_graph) -> None:
        assert is_sparse(isolated_graph)

    def test_triangle_dense(self, triangle_graph) -> None:
        assert is_dense(triangle_graph)

    def test_sparse_not_dense(self, isolated_graph) -> None:
        assert not is_dense(isolated_graph)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class TestDensity:
    def test_connected(self, connected_graph) -> None:
        assert density(connected_graph) == pytest.approx(0.4666666666666667)

    def test_complete(self, triangle_graph) -> None:
        assert density(triangle_graph) == pytest.approx(1.0)

    def test_isolated_zero(self, isolated_graph) -> None:
        assert density(isolated_graph) == pytest.approx(0.0)

    def test_single_vertex_zero(self) -> None:
        g = Graph()
        g.add_vertex("A")
        assert density(g) == pytest.approx(0.0)


class TestDiameter:
    def test_big_graph(self, big_graph) -> None:
        assert diameter(big_graph) == 3

    def test_single_edge(self, simple_edge_graph) -> None:
        assert diameter(simple_edge_graph) == 1

    def test_disconnected_zero(self, isolated_graph) -> None:
        assert diameter(isolated_graph) == 0


# ---------------------------------------------------------------------------
# Matrix operations
# ---------------------------------------------------------------------------


class TestInvert:
    def test_zeros_to_ones(self) -> None:
        assert invert([[0, 0], [0, 0]]) == [[1, 1], [1, 1]]

    def test_ones_to_zeros(self) -> None:
        assert invert([[1, 1], [1, 1]]) == [[0, 0], [0, 0]]

    def test_own_inverse(self) -> None:
        original = [[0, 1], [0, 0]]
        assert invert(invert(original)) == original


class TestGetComplement:
    def test_label(self, isolated_graph) -> None:
        assert "complement" in get_complement(isolated_graph).label

    def test_isolated_has_cross_edges(self, isolated_graph) -> None:
        c = get_complement(isolated_graph)
        cross = [e for e in c.edges() if e.source != e.target]
        assert len(cross) > 0

    def test_complete_only_self_loops(self, triangle_graph) -> None:
        c = get_complement(triangle_graph)
        cross = [e for e in c.edges() if e.source != e.target]
        assert len(cross) == 0

    def test_vertex_count_preserved(self, big_graph) -> None:
        assert get_complement(big_graph).order == big_graph.order
