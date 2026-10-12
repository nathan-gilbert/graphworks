"""Unit tests for :mod:`graphworks.algorithms.search`."""

from __future__ import annotations

import json

import pytest

from graphworks.algorithms.search import breadth_first_search, depth_first_search
from graphworks.graph import Graph


class TestBreadthFirstSearch:
    def test_bfs_from_c(self, search_graph) -> None:
        assert breadth_first_search(search_graph, "c") == ["c", "a", "b", "d"]

    def test_visits_all(self, search_graph) -> None:
        assert sorted(breadth_first_search(search_graph, "a")) == ["a", "b", "c", "d"]

    def test_single_vertex(self) -> None:
        g = Graph(input_graph=json.dumps({"graph": {"x": []}}))
        assert breadth_first_search(g, "x") == ["x"]

    def test_start_is_first(self, search_graph) -> None:
        assert breadth_first_search(search_graph, "b")[0] == "b"

    def test_no_duplicates(self, search_graph) -> None:
        walk = breadth_first_search(search_graph, "a")
        assert len(walk) == len(set(walk))

    def test_missing_start(self, search_graph) -> None:
        with pytest.raises(KeyError):
            breadth_first_search(search_graph, "z")

    def test_undirected_reaches_back(self) -> None:
        g = Graph().add_edge("A", "B").add_edge("B", "C")
        assert breadth_first_search(g, "C") == ["C", "B", "A"]


class TestDepthFirstSearch:
    def test_dfs_from_c(self, search_graph) -> None:
        assert depth_first_search(search_graph, "c") == ["c", "d", "b", "a"]

    def test_visits_all(self, search_graph) -> None:
        assert sorted(depth_first_search(search_graph, "a")) == ["a", "b", "c", "d"]

    def test_start_is_first(self, search_graph) -> None:
        assert depth_first_search(search_graph, "a")[0] == "a"

    def test_no_duplicates(self, search_graph) -> None:
        walk = depth_first_search(search_graph, "a")
        assert len(walk) == len(set(walk))

    def test_shared_neighbour_visited_once(self) -> None:
        data = {"graph": {"a": ["b", "c"], "b": [], "c": ["b"]}}
        walk = depth_first_search(Graph(input_graph=json.dumps(data)), "a")
        assert walk.count("b") == 1

    def test_missing_start(self, search_graph) -> None:
        with pytest.raises(KeyError):
            depth_first_search(search_graph, "z")
