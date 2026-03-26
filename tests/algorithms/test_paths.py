"""Unit tests for :mod:`graphworks.algorithms.paths`."""

from __future__ import annotations

import json

import pytest

from graphworks.algorithms.paths import (
    find_all_paths,
    find_isolated_vertices,
    find_path,
    generate_edges,
)
from graphworks.graph import Graph


class TestGenerateEdges:
    def test_single_edge(self) -> None:
        data = {"graph": {"A": ["B"], "B": []}}
        assert len(generate_edges(Graph(input_graph=json.dumps(data)))) == 1

    def test_no_edges(self, isolated_graph) -> None:
        assert generate_edges(isolated_graph) == []

    def test_matches_graph_edges(self, big_graph) -> None:
        assert generate_edges(big_graph) == big_graph.edges()


class TestFindIsolatedVertices:
    def test_all_isolated(self, isolated_graph) -> None:
        assert sorted(find_isolated_vertices(isolated_graph)) == ["a", "b", "c"]

    def test_partial(self) -> None:
        data = {"graph": {"A": ["B"], "B": ["A"], "C": []}}
        assert find_isolated_vertices(Graph(input_graph=json.dumps(data))) == ["C"]

    def test_none_isolated(self, big_graph) -> None:
        assert find_isolated_vertices(big_graph) == []


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
        assert find_path(path_graph, "z", "a") == []


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
        assert find_all_paths(multi_path_graph, "z", "b") == []

    def test_same_start_end(self, multi_path_graph) -> None:
        assert find_all_paths(multi_path_graph, "a", "a") == [["a"]]
