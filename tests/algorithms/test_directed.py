"""Unit tests for :mod:`graphworks.algorithms.directed`."""

from __future__ import annotations

import json

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
        assert circuit == ["A", "C", "B", "A"]
