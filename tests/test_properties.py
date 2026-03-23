"""
tests.test_properties
~~~~~~~~~~~~~~~~~~~~~

Unit tests for :mod:`graphworks.algorithms.properties`.

Covers degree helpers, sequence predicates, structural predicates,
density/diameter metrics, and matrix operations.

Implementation notes on tested behaviour
-----------------------------------------
* ``is_degree_sequence`` — requires the sum of the sequence to be **even**
  and the sequence to be non-increasing.  ``[3, 1, 1]`` has an odd sum (5)
  and therefore returns ``False``.

* ``is_simple`` — checks only for **self-loops** (a vertex listed in its own
  adjacency list).  A graph with a cycle but no self-loop (e.g. the lollipop
  graph) is considered simple by this predicate.

* ``invert`` / ``get_complement`` — ``invert`` flips every cell in the
  adjacency matrix including the diagonal, so the complement of an isolated
  graph contains both cross-edges *and* self-loops.  Tests reflect this
  documented behaviour.

:author: Nathan Gilbert
"""

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
    """Tests for vertex_degree."""

    def test_degree_without_self_loop(self) -> None:
        """Vertex with no self-loop has degree equal to its out-edge count.

        :return: None
        :rtype: None
        """
        data = {"graph": {"a": ["b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(data))
        assert vertex_degree(graph, "b") == 1

    def test_self_loop_counts_twice(self) -> None:
        """A self-loop contributes 2 to the vertex degree.

        :return: None
        :rtype: None
        """
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(data))
        # self-loop (×2) + b + c = 4
        assert vertex_degree(graph, "a") == 4

    def test_isolated_vertex_degree_zero(self, isolated_graph) -> None:
        """An isolated vertex has degree 0.

        :return: None
        :rtype: None
        """
        assert vertex_degree(isolated_graph, "a") == 0

    def test_vertex_with_multiple_neighbours(self, big_graph) -> None:
        """A hub vertex has degree equal to its neighbour count.

        :return: None
        :rtype: None
        """
        # vertex 'c' in big_graph has neighbours: a, b, d, e → degree 4
        assert vertex_degree(big_graph, "c") == 4


class TestMinMaxDegree:
    """Tests for min_degree and max_degree."""

    def test_min_degree(self) -> None:
        """min_degree returns the smallest degree in the graph.

        :return: None
        :rtype: None
        """
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(data))
        assert min_degree(graph) == 1

    def test_max_degree(self) -> None:
        """max_degree returns the largest degree in the graph.

        :return: None
        :rtype: None
        """
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(data))
        assert max_degree(graph) == 4

    def test_min_equals_max_for_regular_graph(self, isolated_graph) -> None:
        """min_degree and max_degree are equal for a regular graph.

        :return: None
        :rtype: None
        """
        assert min_degree(isolated_graph) == max_degree(isolated_graph)

    def test_min_less_than_max_for_irregular(self, big_graph) -> None:
        """min_degree < max_degree for an irregular graph.

        :return: None
        :rtype: None
        """
        assert min_degree(big_graph) < max_degree(big_graph)


class TestDegreeSequence:
    """Tests for degree_sequence."""

    def test_sequence_is_sorted_descending(self) -> None:
        """degree_sequence returns degrees in non-increasing order.

        :return: None
        :rtype: None
        """
        data = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(data))
        seq = degree_sequence(graph)
        assert seq == (4, 1, 1)
        assert list(seq) == sorted(seq, reverse=True)

    def test_isolated_graph_all_zeros(self, isolated_graph) -> None:
        """All-isolated graph has a degree sequence of all zeros.

        :return: None
        :rtype: None
        """
        assert all(d == 0 for d in degree_sequence(isolated_graph))


# ---------------------------------------------------------------------------
# Sequence predicates
# ---------------------------------------------------------------------------


class TestIsDegreeSequence:
    """Tests for is_degree_sequence.

    A valid degree sequence must:
      * be non-increasing, AND
      * have an even sum (handshaking lemma).

    Note: ``[3, 1, 1]`` sums to 5 (odd) → ``False``.
    """

    @pytest.mark.parametrize(
        "seq,expected",
        [
            ([], True),
            ([2, 2], True),  # sum=4 (even), non-increasing
            ([4, 2, 2], True),  # sum=8 (even), non-increasing
            ([1, 2, 3], False),  # not non-increasing
            ([3, 1, 1], False),  # sum=5 (odd)
            ([1], False),  # sum=1 (odd)
            ([0, 0, 0], True),  # all-zero, sum=0 (even)
        ],
    )
    def test_various_sequences(self, seq: list[int], expected: bool) -> None:
        """Parametrised check for valid and invalid degree sequences.

        :param seq: Candidate degree sequence.
        :type seq: list[int]
        :param expected: Expected return value.
        :type expected: bool
        :return: None
        :rtype: None
        """
        assert is_degree_sequence(seq) is expected


class TestIsErdosGallai:
    """Tests for is_erdos_gallai."""

    @pytest.mark.parametrize(
        "seq,expected",
        [
            ([], True),
            ([1], False),  # odd sum
            ([2, 2, 4], False),  # violates EG condition
            ([32, 8, 4, 2, 2], False),
            ([6, 6, 6, 6, 5, 5, 2, 2], True),  # graphical sequence
            ([0, 0, 0], True),  # empty graph on 3 vertices
            ([1, 1], True),  # K₂: two vertices each of degree 1
        ],
    )
    def test_various_sequences(self, seq: list[int], expected: bool) -> None:
        """Parametrised check of the Erdős–Gallai theorem.

        :param seq: Candidate degree sequence.
        :type seq: list[int]
        :param expected: Expected return value.
        :type expected: bool
        :return: None
        :rtype: None
        """
        assert is_erdos_gallai(seq) is expected


# ---------------------------------------------------------------------------
# Structural predicates
# ---------------------------------------------------------------------------


class TestIsRegular:
    """Tests for is_regular."""

    def test_isolated_graph_is_regular(self, isolated_graph) -> None:
        """All-isolated graph is regular (all degrees are 0).

        :return: None
        :rtype: None
        """
        assert is_regular(isolated_graph)

    def test_complete_triangle_is_regular(self, triangle_graph) -> None:
        """Complete graph K₃ is 2-regular.

        :return: None
        :rtype: None
        """
        assert is_regular(triangle_graph)

    def test_irregular_graph(self, big_graph) -> None:
        """Graph with mixed degrees is not regular.

        :return: None
        :rtype: None
        """
        assert not is_regular(big_graph)


class TestIsSimple:
    """Tests for is_simple.

    ``is_simple`` returns ``True`` when **no vertex appears in its own
    neighbour list** (i.e. no self-loop).  A graph may contain cycles and
    still be considered simple by this predicate.
    """

    def test_straight_line_is_simple(self, straight_line_json) -> None:
        """A path graph with no self-loops is simple.

        :return: None
        :rtype: None
        """
        graph = Graph(input_graph=json.dumps(straight_line_json))
        assert is_simple(graph)

    def test_lollipop_graph_is_simple(self, lollipop_json) -> None:
        """The lollipop graph has a cycle but no self-loop, so is simple.

        :return: None
        :rtype: None
        """
        graph = Graph(input_graph=json.dumps(lollipop_json))
        assert is_simple(graph)

    def test_self_loop_makes_graph_not_simple(self, self_loop_json) -> None:
        """A graph where a vertex lists itself as a neighbour is not simple.

        :return: None
        :rtype: None
        """
        graph = Graph(input_graph=json.dumps(self_loop_json))
        assert not is_simple(graph)

    def test_connected_graph_with_self_loops_not_simple(self, connected_json) -> None:
        """The connected fixture includes self-loops so it is not simple.

        :return: None
        :rtype: None
        """
        graph = Graph(input_graph=json.dumps(connected_json))
        # vertex 'b' has 'b' in its neighbour list; vertex 'c' has 'c'
        assert not is_simple(graph)


class TestIsConnected:
    """Tests for is_connected."""

    def test_connected_graph(self, connected_graph) -> None:
        """A connected graph returns True.

        :return: None
        :rtype: None
        """
        assert is_connected(connected_graph)

    def test_isolated_vertices_not_connected(self, isolated_graph) -> None:
        """Isolated vertices make the graph disconnected.

        :return: None
        :rtype: None
        """
        assert not is_connected(isolated_graph)

    def test_big_graph_is_connected(self, big_graph) -> None:
        """The big_graph fixture is connected.

        :return: None
        :rtype: None
        """
        assert is_connected(big_graph)


class TestIsComplete:
    """Tests for is_complete."""

    def test_triangle_is_complete(self, triangle_graph) -> None:
        """K₃ (triangle) is a complete graph.

        :return: None
        :rtype: None
        """
        assert is_complete(triangle_graph)

    def test_isolated_graph_is_not_complete(self, isolated_graph) -> None:
        """Isolated vertices form an incomplete graph.

        :return: None
        :rtype: None
        """
        assert not is_complete(isolated_graph)

    def test_partial_graph_is_not_complete(self, simple_edge_graph) -> None:
        """A graph missing edges is not complete.

        :return: None
        :rtype: None
        """
        assert not is_complete(simple_edge_graph)

    def test_complete_directed_graph(self) -> None:
        """Complete directed graph (every ordered pair has an arc) is complete.

        :return: None
        :rtype: None
        """
        data = {"directed": True, "graph": {"a": ["b"], "b": ["a"]}}
        graph = Graph(input_graph=json.dumps(data))
        assert is_complete(graph)

    def test_incomplete_directed_graph(self) -> None:
        """Directed graph missing some arcs is not complete.

        :return: None
        :rtype: None
        """
        data = {"directed": True, "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert not is_complete(graph)


class TestIsSparseAndDense:
    """Tests for is_sparse and is_dense."""

    def test_isolated_graph_is_sparse(self, isolated_graph) -> None:
        """Zero-edge graph is sparse.

        :return: None
        :rtype: None
        """
        assert is_sparse(isolated_graph)

    def test_complete_triangle_is_dense(self, triangle_graph) -> None:
        """Complete graph has density 1.0 and is therefore dense.

        :return: None
        :rtype: None
        """
        assert is_dense(triangle_graph)

    def test_sparse_not_dense(self, isolated_graph) -> None:
        """A sparse graph is not dense.

        :return: None
        :rtype: None
        """
        assert not is_dense(isolated_graph)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class TestDensity:
    """Tests for density."""

    def test_connected_graph_density(self, connected_graph) -> None:
        """Density of the connected fixture is approximately 0.467.

        :return: None
        :rtype: None
        """
        assert density(connected_graph) == pytest.approx(0.4666666666666667)

    def test_complete_graph_density(self, triangle_graph) -> None:
        """Density of a complete graph is 1.0.

        :return: None
        :rtype: None
        """
        assert density(triangle_graph) == pytest.approx(1.0)

    def test_isolated_graph_density_zero(self, isolated_graph) -> None:
        """Density of a graph with no edges is 0.0.

        :return: None
        :rtype: None
        """
        assert density(isolated_graph) == pytest.approx(0.0)

    def test_single_vertex_density_zero(self) -> None:
        """Graph with fewer than two vertices has density 0.0.

        :return: None
        :rtype: None
        """
        graph = Graph("g")
        graph.add_vertex("A")
        assert density(graph) == pytest.approx(0.0)


class TestDiameter:
    """Tests for diameter."""

    def test_big_graph_diameter(self, big_graph) -> None:
        """Diameter of the big_graph fixture is 3.

        :return: None
        :rtype: None
        """
        assert diameter(big_graph) == 3

    def test_single_edge_diameter(self, simple_edge_graph) -> None:
        """A graph with one edge has diameter 1.

        :return: None
        :rtype: None
        """
        assert diameter(simple_edge_graph) == 1

    def test_disconnected_graph_diameter_zero(self, isolated_graph) -> None:
        """A graph with no paths between vertices returns diameter 0.

        :return: None
        :rtype: None
        """
        assert diameter(isolated_graph) == 0


# ---------------------------------------------------------------------------
# Matrix operations and complement
# ---------------------------------------------------------------------------


class TestInvert:
    """Tests for the invert (matrix complement) function.

    ``invert`` flips every cell including the main diagonal.
    """

    def test_invert_zeros_to_ones(self) -> None:
        """Inverting a zero matrix produces an all-ones matrix.

        :return: None
        :rtype: None
        """
        assert invert([[0, 0], [0, 0]]) == [[1, 1], [1, 1]]

    def test_invert_ones_to_zeros(self) -> None:
        """Inverting an all-ones matrix produces a zero matrix.

        :return: None
        :rtype: None
        """
        assert invert([[1, 1], [1, 1]]) == [[0, 0], [0, 0]]

    def test_invert_mixed(self) -> None:
        """Invert flips 0↔1 for every cell including diagonal.

        :return: None
        :rtype: None
        """
        assert invert([[0, 1], [1, 0]]) == [[1, 0], [0, 1]]

    def test_invert_is_own_inverse(self) -> None:
        """Applying invert twice returns the original matrix.

        :return: None
        :rtype: None
        """
        original = [[0, 1], [0, 0]]
        assert invert(invert(original)) == original


class TestGetComplement:
    """Tests for get_complement.

    Note: because ``invert`` flips the diagonal, the complement of an
    isolated graph contains **self-loops** in addition to cross-edges.
    The complement of a complete graph similarly gains self-loops.
    This is the documented behaviour of the current ``invert`` implementation.
    """

    def test_complement_label(self, isolated_graph) -> None:
        """Complement label appends ' complement' to the original label.

        :return: None
        :rtype: None
        """
        complement = get_complement(isolated_graph)
        assert "complement" in complement.get_label()

    def test_complement_of_isolated_has_cross_edges(self, isolated_graph) -> None:
        """Complement of an isolated graph has edges between distinct vertices.

        The complement matrix has 1s everywhere (including the diagonal), so
        the complement graph contains both cross-edges and self-loops.

        :return: None
        :rtype: None
        """
        complement = get_complement(isolated_graph)
        cross_edges = [e for e in complement.edges() if e.vertex1 != e.vertex2]
        assert len(cross_edges) > 0

    def test_complement_of_complete_has_only_self_loops(self, triangle_graph) -> None:
        """Complement of a complete K₃ has no cross-edges (only diagonal).

        K₃ adjacency matrix has 1s everywhere except the diagonal; inverting
        gives 1s only on the diagonal → only self-loops remain.

        :return: None
        :rtype: None
        """
        complement = get_complement(triangle_graph)
        cross_edges = [e for e in complement.edges() if e.vertex1 != e.vertex2]
        assert len(cross_edges) == 0

    def test_complement_vertex_count_preserved(self, big_graph) -> None:
        """Complement has the same number of vertices as the original.

        :return: None
        :rtype: None
        """
        complement = get_complement(big_graph)
        assert complement.order() == big_graph.order()
