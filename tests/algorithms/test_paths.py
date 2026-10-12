"""Unit tests for :mod:`graphworks.algorithms.paths`."""

from __future__ import annotations

import json

import pytest

from graphworks.algorithms.paths import (
    find_all_paths,
    find_isolated_vertices,
    find_path,
)
from graphworks.graph import Graph


class TestFindIsolatedVertices:
    def test_all_isolated(self, isolated_graph) -> None:
        assert sorted(find_isolated_vertices(isolated_graph)) == ["a", "b", "c"]

    def test_partial(self) -> None:
        data = {"graph": {"A": ["B"], "B": ["A"], "C": []}}
        assert find_isolated_vertices(Graph(input_graph=json.dumps(data))) == ["C"]

    def test_none_isolated(self, big_graph) -> None:
        assert find_isolated_vertices(big_graph) == []

    def test_undirected_edge_declared_once(self) -> None:
        g = Graph().add_edge("A", "B").add_vertex("C")
        assert find_isolated_vertices(g) == ["C"]

    def test_directed_sink_not_isolated(self) -> None:
        g = Graph(directed=True).add_edge("A", "B").add_vertex("C")
        assert find_isolated_vertices(g) == ["C"]


class TestFindPath:
    @pytest.fixture
    def path_graph(self) -> Graph:
        data = {
            "directed": False,
            "graph": {
                "a": ["d"],
                "b": ["c"],
                "c": ["b", "c", "d", "e"],
                "d": ["a", "c"],
                "e": ["c"],
                "f": [],
            },
        }
        return Graph(input_graph=json.dumps(data))

    def test_path_exists(self, path_graph) -> None:
        assert find_path(path_graph, "a", "b") == ["a", "d", "c", "b"]

    def test_no_path(self, path_graph) -> None:
        assert find_path(path_graph, "a", "f") == []

    def test_same_start_end(self, path_graph) -> None:
        assert find_path(path_graph, "c", "c") == ["c"]

    def test_missing_start(self, path_graph) -> None:
        with pytest.raises(KeyError):
            find_path(path_graph, "z", "a")

    def test_missing_end(self, path_graph) -> None:
        with pytest.raises(KeyError):
            find_path(path_graph, "a", "z")

    def test_undirected_path_walks_back(self) -> None:
        g = Graph().add_edge("A", "B").add_edge("B", "C")
        assert find_path(g, "C", "A") == ["C", "B", "A"]

    def test_directed_path_respects_direction(self) -> None:
        g = Graph(directed=True).add_edge("A", "B").add_edge("B", "C")
        assert find_path(g, "C", "A") == []


class TestFindAllPaths:
    @pytest.fixture
    def multi_path_graph(self) -> Graph:
        data = {
            "directed": False,
            "graph": {
                "a": ["d", "f"],
                "b": ["c"],
                "c": ["b", "c", "d", "e"],
                "d": ["a", "c"],
                "e": ["c"],
                "f": ["d"],
            },
        }
        return Graph(input_graph=json.dumps(data))

    def test_multiple_paths(self, multi_path_graph) -> None:
        paths = find_all_paths(multi_path_graph, "a", "b")
        assert paths == [["a", "d", "c", "b"], ["a", "f", "d", "c", "b"]]

    def test_missing_start(self, multi_path_graph) -> None:
        with pytest.raises(KeyError):
            find_all_paths(multi_path_graph, "z", "b")

    def test_no_path(self) -> None:
        g = Graph().add_vertex("A").add_vertex("B")
        assert find_all_paths(g, "A", "B") == []

    def test_same_start_end(self, multi_path_graph) -> None:
        assert find_all_paths(multi_path_graph, "a", "a") == [["a"]]
