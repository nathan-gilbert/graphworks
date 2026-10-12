"""Unit tests for :mod:`graphworks.algorithms.sort`."""

from __future__ import annotations

import json

import pytest

from graphworks.algorithms.sort import topological_sort
from graphworks.graph import Graph


class TestTopologicalSort:
    def test_standard_dag(self, directed_dag) -> None:
        assert topological_sort(directed_dag) == ["F", "E", "C", "D", "B", "A"]

    def test_valid_order(self, directed_dag) -> None:
        result = topological_sort(directed_dag)
        position = {v: i for i, v in enumerate(result)}
        for v in directed_dag.vertices():
            for n in directed_dag.neighbors(v):
                assert position[v] < position[n]

    def test_all_vertices_present(self, directed_dag) -> None:
        assert sorted(topological_sort(directed_dag)) == sorted(directed_dag.vertices())

    def test_linear_chain(self) -> None:
        data = {"directed": True, "graph": {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}}
        assert topological_sort(Graph(input_graph=json.dumps(data))) == ["A", "B", "C", "D"]

    def test_single_vertex(self) -> None:
        data = {"directed": True, "graph": {"A": []}}
        assert topological_sort(Graph(input_graph=json.dumps(data))) == ["A"]

    def test_parallel_roots(self) -> None:
        data = {"directed": True, "graph": {"A": ["C"], "B": ["C"], "C": []}}
        result = topological_sort(Graph(input_graph=json.dumps(data)))
        assert result.index("C") > result.index("A")
        assert result.index("C") > result.index("B")

    def test_cycle_raises(self, directed_cycle_graph) -> None:
        with pytest.raises(ValueError, match="cycle"):
            topological_sort(directed_cycle_graph)

    def test_self_loop_raises(self) -> None:
        with pytest.raises(ValueError, match="cycle"):
            topological_sort(Graph(directed=True).add_edge("A", "A"))

    def test_undirected_raises(self, big_graph) -> None:
        with pytest.raises(ValueError, match="directed"):
            topological_sort(big_graph)
