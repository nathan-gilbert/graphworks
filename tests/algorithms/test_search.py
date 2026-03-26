"""Unit tests for :mod:`graphworks.algorithms.search`."""

from __future__ import annotations

import json

from graphworks.algorithms.search import (
    arrival_departure_dfs,
    breadth_first_search,
    depth_first_search,
)
from graphworks.graph import Graph


class TestBreadthFirstSearch:
    def test_bfs_from_c(self, search_graph) -> None:
        assert breadth_first_search(search_graph, "c") == ["c", "a", "d", "b"]

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


class TestDepthFirstSearch:
    def test_dfs_from_c(self, search_graph) -> None:
        assert depth_first_search(search_graph, "c") == ["c", "d", "a", "b"]

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


class TestArrivalDepartureDFS:
    def _run(self, graph):
        arrival = dict.fromkeys(graph.vertices(), 0)
        departure = dict.fromkeys(graph.vertices(), 0)
        discovered = dict.fromkeys(graph.vertices(), False)
        time = -1
        for v in graph.vertices():
            if not discovered[v]:
                time = arrival_departure_dfs(graph, v, discovered, arrival, departure, time)
        return arrival, departure, discovered

    def test_times(self, disjoint_directed_graph) -> None:
        arrival, departure, _ = self._run(disjoint_directed_graph)
        result = list(zip(arrival.values(), departure.values(), strict=False))
        expected = [(0, 11), (1, 2), (3, 10), (4, 7), (8, 9), (5, 6), (12, 15), (13, 14)]
        assert result == expected

    def test_all_discovered(self, disjoint_directed_graph) -> None:
        _, _, discovered = self._run(disjoint_directed_graph)
        assert all(discovered.values())

    def test_departure_after_arrival(self, disjoint_directed_graph) -> None:
        arrival, departure, _ = self._run(disjoint_directed_graph)
        for v in disjoint_directed_graph.vertices():
            assert departure[v] > arrival[v]

    def test_unique_times(self, disjoint_directed_graph) -> None:
        arrival, departure, _ = self._run(disjoint_directed_graph)
        all_times = list(arrival.values()) + list(departure.values())
        assert len(all_times) == len(set(all_times))
