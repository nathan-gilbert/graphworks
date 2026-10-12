"""Unit tests for :class:`graphworks.graph.Graph`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphworks.edge import Edge
from graphworks.graph import Graph
from graphworks.vertex import Vertex

# ---------------------------------------------------------------------------
# Label, repr, and str
# ---------------------------------------------------------------------------


class TestGraphMetadata:
    def test_label_from_positional_arg(self) -> None:
        assert Graph("my graph").label == "my graph"

    def test_label_defaults_to_empty(self) -> None:
        assert Graph().label == ""

    def test_directed_default(self) -> None:
        assert not Graph().directed

    def test_directed_from_constructor(self) -> None:
        assert Graph(directed=True).directed

    def test_weighted_default(self) -> None:
        assert not Graph().weighted

    def test_repr(self) -> None:
        g = Graph("demo")
        g.add_vertex("A")
        assert "demo" in repr(g)
        assert "order=1" in repr(g)

    def test_str_shows_adjacency_list(self, simple_edge_json) -> None:
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        assert str(graph) == "my graph\nA -> B\nB -> A"

    def test_str_empty_vertex_shows_zero(self) -> None:
        graph = Graph("g")
        graph.add_vertex("X")
        assert "X -> 0" in str(graph)

    def test_str_sorted(self) -> None:
        data = {"label": "g", "graph": {"B": ["A"], "A": []}}
        lines = str(Graph(input_graph=json.dumps(data))).splitlines()
        assert lines[1].startswith("A")
        assert lines[2].startswith("B")

    def test_str_separates_neighbors(self) -> None:
        g = Graph("s").add_edge("AB", "C").add_edge("AB", "D")
        assert "AB -> C, D" in str(g)


# ---------------------------------------------------------------------------
# Construction — JSON
# ---------------------------------------------------------------------------


class TestJsonConstruction:
    def test_label_parsed(self, simple_edge_json) -> None:
        assert Graph(input_graph=json.dumps(simple_edge_json)).label == "my graph"

    def test_undirected_default(self, simple_edge_json) -> None:
        assert not Graph(input_graph=json.dumps(simple_edge_json)).directed

    def test_directed_parsed(self) -> None:
        data = {"directed": True, "graph": {"X": ["Y"], "Y": []}}
        assert Graph(input_graph=json.dumps(data)).directed

    def test_weighted_parsed(self) -> None:
        data = {"weighted": True, "graph": {"X": [], "Y": []}}
        assert Graph(input_graph=json.dumps(data)).weighted

    def test_edge_produced(self, simple_edge_json) -> None:
        graph = Graph(input_graph=json.dumps(simple_edge_json))
        edges = graph.edges()
        assert len(edges) == 1
        assert edges[0].source == "A"
        assert edges[0].target == "B"

    def test_invalid_edge_raises(self) -> None:
        bad = {"graph": {"A": ["B", "C", "D"], "B": []}}
        with pytest.raises(ValueError):  # noqa: PT011
            Graph(input_graph=json.dumps(bad))


class TestFileConstruction:
    def test_read_from_file(self, tmp_dir: Path, simple_edge_json) -> None:
        path = tmp_dir / "g.json"
        path.write_text(json.dumps(simple_edge_json), encoding="utf-8")
        graph = Graph(input_file=str(path))
        assert graph.label == "my graph"
        assert graph.order == 2


# ---------------------------------------------------------------------------
# Construction — matrix
# ---------------------------------------------------------------------------


class TestMatrixConstruction:
    def test_symmetric_matrix(self) -> None:
        graph = Graph(input_matrix=[[0, 1], [1, 0]])
        assert graph.order == 2
        assert graph.size == 1

    def test_zero_matrix(self) -> None:
        assert Graph(input_matrix=[[0, 0], [0, 0]]).size == 0

    def test_non_square_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            Graph(input_matrix=[[0, 1, 0], [1, 0]])

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            Graph(input_matrix=[])

    def test_uuid_vertex_names(self) -> None:
        graph = Graph(input_matrix=[[0, 1], [1, 0]])
        assert all(len(v) == 36 for v in graph.vertices())


# ---------------------------------------------------------------------------
# Vertex manipulation
# ---------------------------------------------------------------------------


class TestVertexManipulation:
    def test_add_vertex_string(self) -> None:
        g = Graph()
        g.add_vertex("A")
        assert g.vertices() == ["A"]

    def test_add_vertex_object(self) -> None:
        g = Graph()
        g.add_vertex(Vertex.create("hub", label="Central", attrs={"rank": 1}))
        v = g.vertex("hub")
        assert v is not None
        assert v.label == "Central"

    def test_duplicate_vertex_idempotent(self) -> None:
        g = Graph()
        g.add_vertex("A")
        g.add_vertex("A")
        assert g.vertices().count("A") == 1

    def test_vertex_lookup(self) -> None:
        g = Graph()
        g.add_vertex("A")
        assert g.vertex("A") is not None
        assert g.vertex("Z") is None

    def test_contains(self) -> None:
        g = Graph()
        g.add_vertex("A")
        assert "A" in g
        assert "Z" not in g

    def test_len(self) -> None:
        g = Graph()
        g.add_vertex("A")
        g.add_vertex("B")
        assert len(g) == 2


# ---------------------------------------------------------------------------
# Edge manipulation
# ---------------------------------------------------------------------------


class TestEdgeManipulation:
    def test_add_edge(self) -> None:
        g = Graph()
        g.add_edge("A", "B")
        assert g.size == 1
        assert g.order == 2

    def test_add_edge_auto_creates_vertices(self) -> None:
        g = Graph()
        g.add_edge("X", "Y")
        assert set(g.vertices()) == {"X", "Y"}

    def test_add_edge_with_weight(self) -> None:
        g = Graph()
        g.add_edge("A", "B", weight=3.5)
        e = g.edge("A", "B")
        assert e is not None
        assert e.weight == pytest.approx(3.5)

    def test_add_edge_with_label(self) -> None:
        g = Graph()
        g.add_edge("A", "B", label="highway")
        e = g.edge("A", "B")
        assert e is not None
        assert e.label == "highway"

    def test_edge_lookup(self) -> None:
        g = Graph()
        g.add_edge("A", "B")
        assert g.edge("A", "B") is not None

    def test_edge_undirected_reverse_lookup(self) -> None:
        g = Graph()
        g.add_edge("A", "B")
        assert g.edge("B", "A") is not None

    def test_edge_directed_no_reverse(self) -> None:
        data = {"directed": True, "graph": {"A": ["B"], "B": []}}
        g = Graph(input_graph=json.dumps(data))
        assert g.edge("A", "B") is not None
        assert g.edge("B", "A") is None

    def test_edge_missing(self) -> None:
        g = Graph()
        g.add_vertex("A")
        g.add_vertex("B")
        assert g.edge("A", "B") is None

    def test_edges_return_edge_objects(self, simple_edge_graph) -> None:
        edges = simple_edge_graph.edges()
        assert len(edges) == 1
        assert isinstance(edges[0], Edge)


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


class TestGraphProperties:
    def test_order(self, simple_edge_graph) -> None:
        assert simple_edge_graph.order == 2

    def test_size(self, simple_edge_graph) -> None:
        assert simple_edge_graph.size == 1

    def test_neighbors(self, simple_edge_graph) -> None:
        assert simple_edge_graph.neighbors("A") == ["B"]
        assert simple_edge_graph.neighbors("B") == ["A"]

    def test_neighbors_directed_one_way(self) -> None:
        g = Graph(directed=True).add_edge("A", "B")
        assert g.neighbors("A") == ["B"]
        assert g.neighbors("B") == []

    def test_neighbors_missing_vertex(self) -> None:
        with pytest.raises(KeyError):
            Graph().neighbors("Z")


# ---------------------------------------------------------------------------
# Adjacency matrix
# ---------------------------------------------------------------------------


class TestAdjacencyMatrix:
    def test_values(self, simple_edge_graph) -> None:
        assert simple_edge_graph.adjacency_matrix() == [[0, 1], [1, 0]]

    def test_square(self, big_graph) -> None:
        n = big_graph.order
        matrix = big_graph.adjacency_matrix()
        assert len(matrix) == n
        assert all(len(row) == n for row in matrix)

    def test_index_roundtrip(self, simple_edge_graph) -> None:
        for v in simple_edge_graph.vertices():
            idx = simple_edge_graph.vertex_to_index(v)
            assert simple_edge_graph.index_to_vertex(idx) == v

    def test_vertex_to_index_missing(self, simple_edge_graph) -> None:
        with pytest.raises(KeyError):
            simple_edge_graph.vertex_to_index("Z")

    def test_directed_asymmetric(self) -> None:
        data = {"directed": True, "graph": {"A": ["B"], "B": []}}
        matrix = Graph(input_graph=json.dumps(data)).adjacency_matrix()
        assert matrix[0][1] == 1
        assert matrix[1][0] == 0


# ---------------------------------------------------------------------------
# Iteration
# ---------------------------------------------------------------------------


class TestIteration:
    def test_iter_all_vertices(self) -> None:
        data = {"graph": {"A": ["B", "C", "D"], "B": [], "C": [], "D": []}}
        assert sorted(Graph(input_graph=json.dumps(data))) == ["A", "B", "C", "D"]

    def test_getitem_returns_neighbors(self) -> None:
        data = {"graph": {"A": ["B", "C", "D"], "B": [], "C": [], "D": []}}
        g = Graph(input_graph=json.dumps(data))
        assert len(g["A"]) == 3
        assert g["B"] == ["A"]

    def test_getitem_missing(self) -> None:
        with pytest.raises(KeyError):
            Graph()["MISSING"]


# ---------------------------------------------------------------------------
# Undirected symmetry, JSON edge data, and equality
# ---------------------------------------------------------------------------


class TestUndirectedSymmetry:
    def test_add_edge_is_symmetric(self) -> None:
        g = Graph().add_edge("A", "B", weight=2)
        assert g.neighbors("B") == ["A"]
        assert g.edge("A", "B") is g.edge("B", "A")
        assert g.size == 1

    def test_json_one_direction_is_enough(self) -> None:
        g = Graph(input_graph=json.dumps({"graph": {"A": ["B"], "B": []}}))
        assert g.neighbors("B") == ["A"]

    def test_json_both_directions_first_wins(self) -> None:
        data = {
            "graph": {
                "A": [{"target": "B", "weight": 1}],
                "B": [{"target": "A", "weight": 9}],
            }
        }
        g = Graph(input_graph=json.dumps(data))
        assert g.size == 1
        assert g.edge("B", "A").weight == 1

    def test_matrix_input_symmetric(self) -> None:
        g = Graph(input_matrix=[[0, 1], [0, 0]])
        assert g.adjacency_matrix() == [[0, 1], [1, 0]]
        assert g.size == 1

    def test_union_keeps_symmetry(self) -> None:
        merged = Graph().add_edge("A", "B") | Graph().add_edge("B", "C")
        assert sorted(merged.neighbors("B")) == ["A", "C"]


class TestJsonEdgeData:
    def test_neighbor_objects_parsed(self) -> None:
        data = {
            "weighted": True,
            "vertices": {"A": {"label": "Alpha", "attrs": {"x": 1}}},
            "graph": {"A": [{"target": "B", "weight": 2.5, "label": "toll"}], "B": []},
        }
        g = Graph(input_graph=json.dumps(data))
        edge = g.edge("A", "B")
        assert edge is not None
        assert (edge.weight, edge.label) == (2.5, "toll")
        vertex = g.vertex("A")
        assert vertex is not None
        assert vertex.label == "Alpha"
        assert vertex.attrs["x"] == 1

    def test_weighted_fixture(self) -> None:
        g = Graph(input_file=str(Path(__file__).parent / "data" / "g4.json"))
        assert g.edge("B", "C").weight == 3
        assert g.edge("A", "A").weight == 1

    def test_unknown_target_raises(self) -> None:
        with pytest.raises(ValueError, match="not in the graph"):
            Graph(input_graph=json.dumps({"graph": {"A": ["Z"]}}))

    def test_invalid_neighbor_entry_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid neighbor entry"):
            Graph(input_graph=json.dumps({"graph": {"A": [{"weight": 1}], "B": []}}))


class TestGraphEquality:
    def test_equal_structure(self) -> None:
        assert Graph("x").add_edge("A", "B") == Graph("y").add_edge("B", "A")

    def test_weights_ignored(self) -> None:
        assert Graph().add_edge("A", "B", weight=1) == Graph().add_edge("A", "B", weight=2)

    def test_direction_matters(self) -> None:
        assert Graph(directed=True).add_edge("A", "B") != Graph(directed=True).add_edge("B", "A")
        assert Graph().add_edge("A", "B") != Graph(directed=True).add_edge("A", "B")

    def test_vertices_matter(self) -> None:
        assert Graph().add_vertex("A") != Graph().add_vertex("B")

    def test_not_equal_to_other_types(self) -> None:
        assert Graph() != "graph"

    def test_unhashable(self) -> None:
        with pytest.raises(TypeError):
            hash(Graph())
