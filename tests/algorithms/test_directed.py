"""Unit tests for :mod:`graphworks.algorithms.directed`."""

from __future__ import annotations

import json

import pytest

from graphworks.algorithms.directed import find_circuit, is_dag
from graphworks.graph import Graph


class TestIsDag:
    def test_dag_returns_true(self, directed_dag) -> None:
        assert is_dag(directed_dag)

    def test_cyclic_returns_false(self, directed_cycle_graph) -> None:
        assert not is_dag(directed_cycle_graph)

    def test_undirected_returns_false(self, big_graph) -> None:
        assert not is_dag(big_graph)

    def test_removing_cycle_makes_dag(self, directed_cycle_json) -> None:
        directed_cycle_json["graph"]["D"] = ["E"]
        assert is_dag(Graph(input_graph=json.dumps(directed_cycle_json)))

    def test_self_loop_not_dag(self) -> None:
        assert not is_dag(Graph(directed=True).add_edge("A", "A"))

    def test_empty_directed_is_dag(self) -> None:
        assert is_dag(Graph(directed=True))

    def test_linear_dag(self) -> None:
        data = {"directed": True, "graph": {"A": ["B"], "B": ["C"], "C": []}}
        assert is_dag(Graph(input_graph=json.dumps(data)))


class TestFindCircuit:
    def test_simple_circuit(self, circuit_graph) -> None:
        circuit = find_circuit(circuit_graph)
        assert len(circuit) == 4
        assert circuit[0] == circuit[-1]

    def test_visits_all_vertices(self, circuit_graph) -> None:
        assert set(find_circuit(circuit_graph)) == {"A", "B", "C"}

    def test_empty_graph(self) -> None:
        assert find_circuit(Graph()) == []

    def test_specific_order(self, circuit_json) -> None:
        circuit = find_circuit(Graph(input_graph=json.dumps(circuit_json)))
        assert circuit == ["A", "B", "C", "A"]

    def test_follows_edge_direction(self, circuit_graph) -> None:
        circuit = find_circuit(circuit_graph)
        for u, v in zip(circuit, circuit[1:], strict=False):
            assert circuit_graph.edge(u, v) is not None

    def test_no_edges(self, isolated_graph) -> None:
        assert find_circuit(isolated_graph) == []

    def test_undirected_triangle(self, triangle_graph) -> None:
        circuit = find_circuit(triangle_graph)
        assert len(circuit) == 4
        assert circuit[0] == circuit[-1]
        assert {frozenset(p) for p in zip(circuit, circuit[1:], strict=False)} == {
            frozenset(e) for e in (("a", "b"), ("b", "c"), ("a", "c"))
        }

    def test_undirected_with_self_loop(self) -> None:
        g = Graph().add_edges([("A", "B"), ("B", "C"), ("C", "A"), ("A", "A")])
        circuit = find_circuit(g)
        assert len(circuit) == 5
        assert circuit[0] == circuit[-1]

    def test_path_has_no_circuit(self) -> None:
        g = Graph(directed=True).add_edge("A", "B").add_edge("B", "C")
        with pytest.raises(ValueError, match="unbalanced"):
            find_circuit(g)

    def test_odd_degree_has_no_circuit(self, straight_line_json) -> None:
        with pytest.raises(ValueError, match="unbalanced"):
            find_circuit(Graph(input_graph=json.dumps(straight_line_json)))

    def test_disconnected_cycles_have_no_circuit(self) -> None:
        g = Graph(directed=True).add_edges(
            [("A", "B"), ("B", "A"), ("C", "D"), ("D", "C")],
        )
        with pytest.raises(ValueError, match="not connected"):
            find_circuit(g)
