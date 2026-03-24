"""Unit and integration tests for :class:`graphworks.graph.Graph`.

Covers construction (JSON string, JSON file, adjacency matrix), vertex/edge manipulation,
the stdlib adjacency-matrix interface, validation, iteration, string representations, and the new
first-class :class:`Vertex` / :class:`Edge` access methods.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from graphworks.edge import Edge
from graphworks.graph import Graph
from graphworks.vertex import Vertex

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _edge_pairs(graph: Graph) -> list[tuple[str, str]]:
    """Return the edges of *graph* as ``(source, target)`` tuples.

    :param graph: The graph whose edges to extract.
    :type graph: Graph
    :return: List of ``(source, target)`` pairs.
    :rtype: list[tuple[str, str]]
    """
    return [(e.source, e.target) for e in graph.edges()]


# ---------------------------------------------------------------------------
# Label, repr, and str
# ---------------------------------------------------------------------------


class TestGraphLabel:
    """Tests for graph label, repr, and str behaviour."""

    def test_label_from_positional_arg(self) -> None:
        """Graph label is stored and returned correctly."""
        graph = Graph("my graph")
        assert graph.get_label() == "my graph"

    def test_label_defaults_to_empty_string(self) -> None:
        """Constructing without a label yields an empty string."""
        graph = Graph()
        assert graph.get_label() == ""

    def test_repr_returns_label(self) -> None:
        """repr() of a graph is its label."""
        graph = Graph("demo")
        assert repr(graph) == "demo"

    def test_str_shows_adjacency_list(self, simple_edge_json) -> None:
        """str() renders a labelled, sorted adjacency list."""
        expected = "my graph\nA -> B\nB -> 0"
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        assert str(graph) == expected

    def test_str_empty_vertex_shows_zero(self) -> None:
        """Vertices with no neighbours render as '-> 0'."""
        graph = Graph("g")
        graph.add_vertex("X")
        assert "X -> 0" in str(graph)

    def test_str_multiple_vertices_sorted(self) -> None:
        """str() renders vertices in sorted order."""
        data = {"label": "g", "graph": {"B": ["A"], "A": []}}
        graph = Graph(input_graph=json.dumps(data))
        lines = str(graph).splitlines()
        # First line is label; vertex lines must be sorted
        assert lines[1].startswith("A")
        assert lines[2].startswith("B")


# ---------------------------------------------------------------------------
# Construction — JSON string
# ---------------------------------------------------------------------------


class TestGraphJsonConstruction:
    """Tests for building a Graph from a JSON string."""

    def test_label_parsed(self, simple_edge_json) -> None:
        """JSON 'label' key is correctly stored."""
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        assert graph.get_label() == "my graph"

    def test_undirected_flag_default(self, simple_edge_json) -> None:
        """Graph without 'directed' key is undirected by default."""
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        assert not graph.is_directed()

    def test_adjacency_list_stored(self, simple_edge_json) -> None:
        """get_graph() returns the raw adjacency dict from the JSON."""
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        assert graph.get_graph() == simple_edge_json["graph"]

    def test_edge_is_produced(self, simple_edge_json) -> None:
        """One edge A→B is produced from the JSON definition."""
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        pairs = _edge_pairs(graph)
        assert len(pairs) == 1
        assert pairs[0] == ("A", "B")

    def test_directed_flag_parsed(self) -> None:
        """'directed' key in JSON sets the directed flag."""
        data = {"directed": True, "graph": {"X": ["Y"], "Y": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert graph.is_directed()

    def test_weighted_flag_parsed(self) -> None:
        """'weighted' key in JSON sets the weighted flag."""
        data = {"weighted": True, "graph": {"X": [], "Y": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert graph.is_weighted()

    def test_missing_label_defaults_to_empty(self) -> None:
        """JSON without 'label' key uses empty string as label."""
        data = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert graph.get_label() == ""

    def test_invalid_edge_raises_value_error(self) -> None:
        """Edge referencing a missing vertex raises ValueError."""
        bad = {"graph": {"A": ["B", "C", "D"], "B": []}}
        with pytest.raises(ValueError):  # noqa: PT011
            Graph(input_graph=json.dumps(bad))


# ---------------------------------------------------------------------------
# Construction — JSON file
# ---------------------------------------------------------------------------


class TestGraphFileConstruction:
    """Tests for building a Graph from a JSON file."""

    def test_read_from_file(self, tmp_dir: Path, simple_edge_json) -> None:
        """Graph is correctly loaded from a JSON file on disk."""
        file_path = tmp_dir / "g.json"
        file_path.write_text(json.dumps(simple_edge_json), encoding="utf-8")
        graph = Graph(input_file=str(file_path))
        assert graph.get_label() == "my graph"
        assert not graph.is_directed()
        assert graph.get_graph() == simple_edge_json["graph"]

    def test_file_vertices_match(self, tmp_dir: Path, simple_edge_json) -> None:
        """Vertices loaded from file match the JSON definition."""
        file_path = tmp_dir / "g.json"
        file_path.write_text(json.dumps(simple_edge_json), encoding="utf-8")
        graph = Graph(input_file=str(file_path))
        assert set(graph.vertices()) == {"A", "B"}


# ---------------------------------------------------------------------------
# Construction — stdlib adjacency matrix
# ---------------------------------------------------------------------------


class TestGraphMatrixConstruction:
    """Tests for building a Graph from a stdlib adjacency matrix."""

    def test_simple_two_by_two_matrix(self) -> None:
        """A 2x2 symmetric matrix yields one undirected edge."""
        matrix = [[0, 1], [1, 0]]
        graph = Graph(input_matrix=matrix)
        assert len(graph.vertices()) == 2
        assert len(graph.edges()) == 1

    def test_zero_matrix_no_edges(self) -> None:
        """A zero matrix produces no edges."""
        matrix = [[0, 0], [0, 0]]
        graph = Graph(input_matrix=matrix)
        assert len(graph.edges()) == 0

    def test_non_square_raises_value_error(self) -> None:
        """A non-square matrix raises ValueError."""
        with pytest.raises(ValueError):  # noqa: PT011
            Graph(input_matrix=[[0, 1, 0], [1, 0]])

    def test_wrong_row_count_raises_value_error(self) -> None:
        """A matrix where row count != column count raises ValueError."""
        with pytest.raises(ValueError):  # noqa: PT011
            Graph(input_matrix=[[0, 1], [1, 0], [1, 0]])

    def test_empty_matrix_raises_value_error(self) -> None:
        """An empty matrix raises ValueError."""
        with pytest.raises(ValueError):  # noqa: PT011
            Graph(input_matrix=[])

    def test_vertices_are_uuid_strings(self) -> None:
        """Matrix-constructed graphs use UUID strings as vertex names."""
        graph = Graph(input_matrix=[[0, 1], [1, 0]])
        # UUIDs are 36 characters long
        assert all(len(v) == 36 for v in graph.vertices())


# ---------------------------------------------------------------------------
# Vertex and edge manipulation
# ---------------------------------------------------------------------------


class TestVertexEdgeManipulation:
    """Tests for add_vertex, add_edge, vertices(), edges(), order(), size()."""

    def test_add_single_vertex(self) -> None:
        """Adding a single vertex is reflected in vertices()."""
        graph = Graph("g")
        graph.add_vertex("A")
        assert graph.vertices() == ["A"]

    def test_add_duplicate_vertex_is_idempotent(self) -> None:
        """Adding a vertex that already exists does not duplicate it."""
        graph = Graph("g")
        graph.add_vertex("A")
        graph.add_vertex("A")
        assert graph.vertices().count("A") == 1

    def test_add_edge_between_existing_vertices(self) -> None:
        """add_edge creates one edge between two pre-existing vertices."""
        graph = Graph("g")
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        assert len(graph.edges()) == 1

    def test_add_edge_creates_missing_vertices(self) -> None:
        """add_edge auto-creates vertices that do not yet exist."""
        graph = Graph("g")
        graph.add_edge("X", "Y")
        assert len(graph.edges()) == 1
        assert len(graph.vertices()) == 2

    def test_multiple_edges(self) -> None:
        """Multiple add_edge calls accumulate correctly."""
        graph = Graph("g")
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        graph.add_edge("X", "Y")
        assert len(graph.edges()) == 2
        assert len(graph.vertices()) == 4

    def test_order_and_size(self, simple_edge_graph) -> None:
        """order() and size() return vertex and edge counts."""
        assert simple_edge_graph.order() == 2
        assert simple_edge_graph.size() == 1

    def test_get_neighbors_populated(self, simple_edge_graph) -> None:
        """get_neighbors returns the correct neighbour list."""
        assert simple_edge_graph.get_neighbors("A") == ["B"]

    def test_get_neighbors_empty(self, simple_edge_graph) -> None:
        """get_neighbors returns [] for a vertex with no out-edges."""
        assert simple_edge_graph.get_neighbors("B") == []

    def test_get_random_vertex_is_in_graph(self, big_graph) -> None:
        """get_random_vertex returns a vertex that exists in the graph."""
        v = big_graph.get_random_vertex()
        assert v in big_graph.vertices()

    def test_set_directed(self) -> None:
        """set_directed toggles the is_directed flag."""
        graph = Graph("g")
        graph.add_vertex("A")
        assert not graph.is_directed()
        graph.set_directed(True)
        assert graph.is_directed()
        graph.set_directed(False)
        assert not graph.is_directed()


# ---------------------------------------------------------------------------
# First-class Vertex and Edge access
# ---------------------------------------------------------------------------


class TestFirstClassAccess:
    """Tests for get_vertex, get_vertices, get_edge, and Vertex-based add_vertex."""

    def test_get_vertex_returns_vertex_object(self) -> None:
        """get_vertex returns a Vertex with the correct name."""
        graph = Graph("g")
        graph.add_vertex("A")
        v = graph.get_vertex("A")
        assert v is not None
        assert v.name == "A"

    def test_get_vertex_missing_returns_none(self) -> None:
        """get_vertex returns None for a vertex not in the graph."""
        graph = Graph("g")
        assert graph.get_vertex("Z") is None

    def test_get_vertices_returns_all_objects(self) -> None:
        """get_vertices returns Vertex objects for every vertex."""
        data = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        verts = graph.get_vertices()
        assert len(verts) == 2
        assert all(isinstance(v, Vertex) for v in verts)
        assert {v.name for v in verts} == {"A", "B"}

    def test_add_vertex_with_vertex_object(self) -> None:
        """add_vertex accepts a Vertex instance directly."""
        graph = Graph("g")
        v = Vertex.create("hub", label="Central Hub", attrs={"rank": 1})
        graph.add_vertex(v)
        retrieved = graph.get_vertex("hub")
        assert retrieved is not None
        assert retrieved.label == "Central Hub"
        assert retrieved.attrs["rank"] == 1

    def test_add_vertex_object_idempotent(self) -> None:
        """Adding a Vertex with a name that already exists is a no-op."""
        graph = Graph("g")
        graph.add_vertex(Vertex("A", label="first"))
        graph.add_vertex(Vertex("A", label="second"))
        v = graph.get_vertex("A")
        assert v is not None
        assert v.label == "first"

    def test_get_edge_returns_edge_object(self) -> None:
        """get_edge returns the Edge stored between two vertices."""
        graph = Graph("g")
        graph.add_edge("A", "B")
        e = graph.get_edge("A", "B")
        assert e is not None
        assert e.source == "A"
        assert e.target == "B"

    def test_get_edge_undirected_reverse_lookup(self) -> None:
        """get_edge on an undirected graph finds edge in both directions."""
        graph = Graph("g")
        graph.add_edge("A", "B")
        assert graph.get_edge("B", "A") is not None

    def test_get_edge_directed_no_reverse(self) -> None:
        """get_edge on a directed graph does not find the reverse edge."""
        data = {"directed": True, "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert graph.get_edge("A", "B") is not None
        assert graph.get_edge("B", "A") is None

    def test_get_edge_missing_returns_none(self) -> None:
        """get_edge returns None when no edge exists."""
        graph = Graph("g")
        graph.add_vertex("A")
        graph.add_vertex("B")
        assert graph.get_edge("A", "B") is None

    def test_add_edge_with_weight(self) -> None:
        """add_edge stores a weight on the created Edge."""
        graph = Graph("g")
        graph.add_edge("A", "B", weight=3.5)
        e = graph.get_edge("A", "B")
        assert e is not None
        assert e.weight == pytest.approx(3.5)

    def test_add_edge_with_label(self) -> None:
        """add_edge stores a label on the created Edge."""
        graph = Graph("g")
        graph.add_edge("A", "B", label="highway")
        e = graph.get_edge("A", "B")
        assert e is not None
        assert e.label == "highway"

    def test_edges_return_edge_objects(self, simple_edge_graph) -> None:
        """edges() returns actual Edge instances."""
        edge_list = simple_edge_graph.edges()
        assert len(edge_list) == 1
        e = edge_list[0]
        assert isinstance(e, Edge)
        assert e.source == "A"
        assert e.target == "B"


# ---------------------------------------------------------------------------
# Adjacency matrix interface (stdlib only)
# ---------------------------------------------------------------------------


class TestAdjacencyMatrix:
    """Tests for the stdlib adjacency matrix interface."""

    def test_values_for_simple_edge(self, simple_edge_graph) -> None:
        """Matrix has 1 for A->B and 0 elsewhere."""
        matrix = simple_edge_graph.get_adjacency_matrix()
        assert matrix == [[0, 1], [0, 0]]

    def test_matrix_is_square(self, big_graph) -> None:
        """Adjacency matrix dimensions equal the vertex count."""
        n = big_graph.order()
        matrix = big_graph.get_adjacency_matrix()
        assert len(matrix) == n
        assert all(len(row) == n for row in matrix)

    def test_vertex_index_roundtrip(self, simple_edge_graph) -> None:
        """vertex_to_matrix_index and matrix_index_to_vertex are inverses."""
        for v in simple_edge_graph.vertices():
            idx = simple_edge_graph.vertex_to_matrix_index(v)
            assert simple_edge_graph.matrix_index_to_vertex(idx) == v

    def test_directed_graph_matrix_asymmetric(self) -> None:
        """A directed graph produces an asymmetric adjacency matrix."""
        data = {"directed": True, "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        matrix = graph.get_adjacency_matrix()
        # A->B exists (1) but B->A does not (0)
        assert matrix[0][1] == 1
        assert matrix[1][0] == 0


# ---------------------------------------------------------------------------
# Iteration protocol
# ---------------------------------------------------------------------------


class TestGraphIteration:
    """Tests for __iter__ and __getitem__."""

    def test_iter_visits_all_vertices(self) -> None:
        """Iterating over a graph yields every vertex exactly once."""
        data = {"graph": {"A": ["B", "C", "D"], "B": [], "C": [], "D": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert sorted(graph) == ["A", "B", "C", "D"]

    def test_iter_count(self) -> None:
        """Number of iterations equals the number of vertices."""
        data = {"graph": {"A": ["B", "C", "D"], "B": [], "C": [], "D": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert sum(1 for _ in graph) == 4

    def test_iter_yields_correct_neighbour_counts(self) -> None:
        """Neighbour lists obtained via iteration have correct lengths."""
        data = {"graph": {"A": ["B", "C", "D"], "B": [], "C": [], "D": []}}
        graph = Graph(input_graph=json.dumps(data))
        counts = {key: len(graph[key]) for key in graph}
        assert counts["A"] == 3
        assert counts["B"] == 0

    def test_getitem_returns_neighbours(self) -> None:
        """graph[vertex] returns the neighbour list."""
        data = {"graph": {"A": ["B", "C", "D"], "B": [], "C": [], "D": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert len(graph["A"]) == 3
        assert graph["B"] == []

    def test_getitem_missing_vertex_returns_empty(self) -> None:
        """graph[missing] returns an empty list rather than raising."""
        graph = Graph("g")
        assert graph["MISSING"] == []


# ---------------------------------------------------------------------------
# Backward compatibility — get_graph()
# ---------------------------------------------------------------------------


class TestGetGraphCompat:
    """Tests that get_graph() returns the expected defaultdict structure."""

    def test_get_graph_matches_json_input(self, simple_edge_json) -> None:
        """get_graph() returns the same structure as the original JSON."""
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        result = graph.get_graph()
        assert dict(result) == simple_edge_json["graph"]

    def test_get_graph_is_defaultdict(self, simple_edge_json) -> None:
        """get_graph() returns a defaultdict for backward compat."""
        from collections import defaultdict

        graph = Graph(input_graph=json.dumps(simple_edge_json))
        result = graph.get_graph()
        assert isinstance(result, defaultdict)

    def test_get_graph_undirected_neighbors_symmetric(self) -> None:
        """For an undirected graph, get_graph reflects both directions."""
        data = {"graph": {"A": ["B"], "B": ["A"]}}
        graph = Graph(input_graph=json.dumps(data))
        gg = graph.get_graph()
        assert "B" in gg["A"]
        assert "A" in gg["B"]
