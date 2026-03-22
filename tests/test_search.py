"""
tests.test_search
~~~~~~~~~~~~~~~~~

Unit tests for :mod:`graphworks.algorithms.search`.

Covers breadth_first_search, depth_first_search, and arrival_departure_dfs.

:author: Nathan Gilbert
"""

from __future__ import annotations

import json

from graphworks.algorithms.search import (
    arrival_departure_dfs,
    breadth_first_search,
    depth_first_search,
)
from graphworks.graph import Graph


class TestBreadthFirstSearch:
    """Tests for breadth_first_search."""

    def test_bfs_from_c(self, search_graph) -> None:
        """BFS from 'c' visits all reachable vertices in level order.

        :return: Nothing
        :rtype: None
        """
        walk = breadth_first_search(search_graph, "c")
        assert walk == ["c", "a", "d", "b"]

    def test_bfs_visits_all_vertices(self, search_graph) -> None:
        """BFS visits every vertex in the connected graph.

        :return: Nothing
        :rtype: None
        """
        walk = breadth_first_search(search_graph, "a")
        assert sorted(walk) == ["a", "b", "c", "d"]

    def test_bfs_single_vertex(self) -> None:
        """BFS on a single-vertex graph returns just that vertex.

        :return: Nothing
        :rtype: None
        """
        g = Graph(input_graph=json.dumps({"graph": {"x": []}}))
        assert breadth_first_search(g, "x") == ["x"]

    def test_bfs_start_vertex_is_first(self, search_graph) -> None:
        """BFS walk always begins with the given start vertex.

        :return: Nothing
        :rtype: None
        """
        walk = breadth_first_search(search_graph, "b")
        assert walk[0] == "b"

    def test_bfs_no_duplicates(self, search_graph) -> None:
        """BFS never visits a vertex more than once.

        :return: Nothing
        :rtype: None
        """
        walk = breadth_first_search(search_graph, "a")
        assert len(walk) == len(set(walk))


class TestDepthFirstSearch:
    """Tests for depth_first_search."""

    def test_dfs_from_c(self, search_graph) -> None:
        """DFS from 'c' visits vertices in depth-first order.

        :return: Nothing
        :rtype: None
        """
        walk = depth_first_search(search_graph, "c")
        assert walk == ["c", "d", "a", "b"]

    def test_dfs_visits_all_vertices(self, search_graph) -> None:
        """DFS visits every vertex in the connected graph.

        :return: Nothing
        :rtype: None
        """
        walk = depth_first_search(search_graph, "a")
        assert sorted(walk) == ["a", "b", "c", "d"]

    def test_dfs_start_vertex_is_first(self, search_graph) -> None:
        """DFS walk always begins with the given start vertex.

        :return: Nothing
        :rtype: None
        """
        walk = depth_first_search(search_graph, "a")
        assert walk[0] == "a"

    def test_dfs_no_duplicates(self, search_graph) -> None:
        """DFS never visits a vertex more than once.

        :return: Nothing
        :rtype: None
        """
        walk = depth_first_search(search_graph, "a")
        assert len(walk) == len(set(walk))

    def test_dfs_shared_neighbour_visited_only_once(self) -> None:
        """DFS skips a vertex that was pushed onto the stack twice.

        When two vertices both point at the same neighbour, that neighbour may
        be pushed onto the stack multiple times before being popped.  The
        already-visited guard (``if vertex not in visited``) ensures the vertex
        is processed exactly once even when it is encountered a second time.
        This exercises the ``False`` branch of that guard.

        Graph topology: ``a → [b, c]``, ``c → [b]`` — vertex *b* is reachable
        from both *a* (directly) and *c* (indirectly via *a*'s push of *c*).

        :return: Nothing
        :rtype: None
        """
        data = {"graph": {"a": ["b", "c"], "b": [], "c": ["b"]}}
        graph = Graph(input_graph=json.dumps(data))
        walk = depth_first_search(graph, "a")
        # b must appear exactly once despite being pushed twice
        assert walk.count("b") == 1
        assert sorted(walk) == ["a", "b", "c"]


class TestArrivalDepartureDFS:
    """Tests for arrival_departure_dfs."""

    def _run_full_traversal(
        self, graph: Graph
    ) -> tuple[dict[str, int], dict[str, int], dict[str, bool]]:
        """Helper: run arrival_departure_dfs over all components of *graph*.

        :param graph: The graph to traverse.
        :type graph: Graph
        :return: Tuple of (arrival, departure, discovered) dictionaries.
        :rtype: tuple[dict[str, int], dict[str, int], dict[str, bool]]
        """
        arrival = dict.fromkeys(graph.vertices(), 0)
        departure = dict.fromkeys(graph.vertices(), 0)
        discovered = dict.fromkeys(graph.vertices(), False)
        time = -1
        for v in graph.vertices():
            if not discovered[v]:
                time = arrival_departure_dfs(graph, v, discovered, arrival, departure, time)
        return arrival, departure, discovered

    def test_arrival_departure_times(self, disjoint_directed_graph) -> None:
        """Arrival and departure times are correctly assigned for both components.

        :return: Nothing
        :rtype: None
        """
        arrival, departure, _ = self._run_full_traversal(disjoint_directed_graph)
        result = list(zip(arrival.values(), departure.values(), strict=False))
        expected = [
            (0, 11),
            (1, 2),
            (3, 10),
            (4, 7),
            (8, 9),
            (5, 6),
            (12, 15),
            (13, 14),
        ]
        assert result == expected

    def test_all_vertices_discovered(self, disjoint_directed_graph) -> None:
        """Every vertex is discovered after a full traversal.

        :return: Nothing
        :rtype: None
        """
        _, _, discovered = self._run_full_traversal(disjoint_directed_graph)
        assert all(discovered.values())

    def test_departure_always_after_arrival(self, disjoint_directed_graph) -> None:
        """Departure time is strictly greater than arrival time for every vertex.

        :return: Nothing
        :rtype: None
        """
        arrival, departure, _ = self._run_full_traversal(disjoint_directed_graph)
        for v in disjoint_directed_graph.vertices():
            assert (
                departure[v] > arrival[v]
            ), f"Vertex {v!r}: departure {departure[v]} not > arrival {arrival[v]}"

    def test_times_are_unique(self, disjoint_directed_graph) -> None:
        """No two events (arrival or departure) share the same timestamp.

        :return: Nothing
        :rtype: None
        """
        arrival, departure, _ = self._run_full_traversal(disjoint_directed_graph)
        all_times = list(arrival.values()) + list(departure.values())
        assert len(all_times) == len(set(all_times))
