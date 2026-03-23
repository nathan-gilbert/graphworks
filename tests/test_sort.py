"""
tests.test_sort
~~~~~~~~~~~~~~~

Unit tests for :mod:`graphworks.algorithms.sort`.

Covers the topological sort algorithm.

:author: Nathan Gilbert
"""

from __future__ import annotations

import json

from graphworks.algorithms.sort import topological
from graphworks.graph import Graph


class TestTopologicalSort:
    """Tests for the topological sort algorithm."""

    def test_standard_dag(self, directed_dag) -> None:
        """topological returns a valid topological order for the fixture DAG."""
        result = topological(directed_dag)
        assert result == ["F", "E", "C", "D", "B", "A"]

    def test_result_is_valid_topological_order(self, directed_dag) -> None:
        """Every edge (u→v) has u appearing before v in the result."""
        result = topological(directed_dag)
        position = {v: i for i, v in enumerate(result)}
        for v in directed_dag.vertices():
            for neighbour in directed_dag.get_neighbors(v):
                assert (
                    position[v] < position[neighbour]
                ), f"Edge {v}→{neighbour} is out of order in topological sort"

    def test_all_vertices_present(self, directed_dag) -> None:
        """Every vertex appears exactly once in the topological order."""
        result = topological(directed_dag)
        assert sorted(result) == sorted(directed_dag.vertices())

    def test_linear_chain(self) -> None:
        """A simple A→B→C→D chain sorts as [A, B, C, D]."""
        data = {
            "directed": True,
            "graph": {"A": ["B"], "B": ["C"], "C": ["D"], "D": []},
        }
        graph = Graph(input_graph=json.dumps(data))
        result = topological(graph)
        assert result == ["A", "B", "C", "D"]

    def test_single_vertex(self) -> None:
        """A single-vertex graph sorts as [that vertex]."""
        data = {"directed": True, "graph": {"A": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert topological(graph) == ["A"]

    def test_parallel_roots(self) -> None:
        """Two independent root vertices both appear before their descendants."""
        data = {
            "directed": True,
            "graph": {"A": ["C"], "B": ["C"], "C": []},
        }
        graph = Graph(input_graph=json.dumps(data))
        result = topological(graph)
        assert result.index("C") > result.index("A")
        assert result.index("C") > result.index("B")
