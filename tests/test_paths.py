"""
tests.test_paths
~~~~~~~~~~~~~~~~

Unit tests for :mod:`graphworks.algorithms.paths`.

Covers generate_edges, find_isolated_vertices, find_path, and find_all_paths.

:author: Nathan Gilbert
"""

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
    """Tests for generate_edges."""

    def test_single_edge_graph(self) -> None:
        """generate_edges returns one edge for a one-edge graph."""
        data = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert len(generate_edges(graph)) == 1

    def test_no_edge_graph(self, isolated_graph) -> None:
        """generate_edges returns an empty list for an isolated graph."""
        assert generate_edges(isolated_graph) == []

    def test_matches_graph_edges(self, big_graph) -> None:
        """generate_edges output matches graph.edges()."""
        assert generate_edges(big_graph) == big_graph.edges()


class TestFindIsolatedVertices:
    """Tests for find_isolated_vertices."""

    def test_all_isolated(self, isolated_graph) -> None:
        """Every vertex is isolated when there are no edges."""
        isolated = find_isolated_vertices(isolated_graph)
        assert sorted(isolated) == ["a", "b", "c"]

    def test_partial_isolation(self) -> None:
        """Only the vertex with no neighbours is returned as isolated."""
        data = {"graph": {"A": ["B"], "B": ["A"], "C": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert find_isolated_vertices(graph) == ["C"]

    def test_no_isolated_vertices(self, big_graph) -> None:
        """A fully connected graph has no isolated vertices."""
        assert find_isolated_vertices(big_graph) == []


class TestFindPath:
    """Tests for find_path."""

    @pytest.fixture
    def path_graph(self) -> Graph:
        """Graph used for path-finding tests.

        :return: Constructed Graph.
        :rtype: Graph
        """
        data = {
            "label": "test",
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
        """find_path returns a valid path when one exists."""
        path = find_path(path_graph, "a", "b")
        assert path == ["a", "d", "c", "b"]

    def test_no_path_to_isolated_vertex(self, path_graph) -> None:
        """find_path returns [] when the destination is unreachable."""
        path = find_path(path_graph, "a", "f")
        assert path == []

    def test_same_start_and_end(self, path_graph) -> None:
        """find_path returns [vertex] when start equals end."""
        path = find_path(path_graph, "c", "c")
        assert path == ["c"]

    def test_missing_start_vertex(self, path_graph) -> None:
        """find_path returns [] when the start vertex is not in the graph."""
        path = find_path(path_graph, "z", "a")
        assert path == []


class TestFindAllPaths:
    """Tests for find_all_paths."""

    @pytest.fixture
    def multi_path_graph(self) -> Graph:
        """Graph with multiple paths between vertices.

        :return: Constructed Graph.
        :rtype: Graph
        """
        data = {
            "label": "test2",
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
        """find_all_paths returns all simple paths between two vertices."""
        paths = find_all_paths(multi_path_graph, "a", "b")
        assert paths == [["a", "d", "c", "b"], ["a", "f", "d", "c", "b"]]

    def test_missing_start_returns_empty(self, multi_path_graph) -> None:
        """find_all_paths returns [] when the start vertex is absent."""
        assert find_all_paths(multi_path_graph, "z", "b") == []

    def test_same_start_and_end(self, multi_path_graph) -> None:
        """find_all_paths([v, v]) returns a single path containing only v."""
        paths = find_all_paths(multi_path_graph, "a", "a")
        assert paths == [["a"]]
