"""
tests.test_directed
~~~~~~~~~~~~~~~~~~~

Unit tests for :mod:`graphworks.algorithms.directed`.

Covers is_dag and find_circuit (Hierholzer's algorithm).

:author: Nathan Gilbert
"""

from __future__ import annotations

import json

from src.graphworks.algorithms.directed import find_circuit, is_dag
from src.graphworks.graph import Graph


class TestIsDag:
    """Tests for is_dag."""

    def test_dag_returns_true(self, directed_dag) -> None:
        """A directed acyclic graph returns True."""
        assert is_dag(directed_dag)

    def test_cyclic_graph_returns_false(self, directed_cycle_graph) -> None:
        """A directed graph with a back-edge returns False."""
        assert not is_dag(directed_cycle_graph)

    def test_undirected_graph_returns_false(self, big_graph) -> None:
        """is_dag returns False for undirected graphs."""
        assert not is_dag(big_graph)

    def test_removing_cycle_makes_dag(self, directed_cycle_json) -> None:
        """Removing the back-edge from a cyclic graph makes it a DAG."""
        directed_cycle_json["graph"]["D"] = ["E"]  # break A→B→D→A
        graph = Graph(input_graph=json.dumps(directed_cycle_json))
        assert is_dag(graph)

    def test_simple_linear_dag(self) -> None:
        """A simple A→B→C chain is a DAG."""
        data = {"directed": True, "graph": {"A": ["B"], "B": ["C"], "C": []}}
        graph = Graph(input_graph=json.dumps(data))
        assert is_dag(graph)


class TestFindCircuit:
    """Tests for find_circuit (Hierholzer's algorithm)."""

    def test_simple_circuit(self, circuit_graph) -> None:
        """Eulerian circuit A→B→C→A is found correctly."""
        circuit = find_circuit(circuit_graph)
        # Hierholzer may return any valid rotation; check structure
        assert len(circuit) == 4
        assert circuit[0] == circuit[-1]  # circuit forms a closed loop

    def test_circuit_visits_all_vertices(self, circuit_graph) -> None:
        """Every vertex appears in the circuit."""
        circuit = find_circuit(circuit_graph)
        assert set(circuit) == {"A", "B", "C"}

    def test_empty_graph_returns_empty(self) -> None:
        """find_circuit on an empty graph returns an empty list."""
        graph = Graph("empty")
        assert find_circuit(graph) == []

    def test_specific_circuit_order(self, circuit_json) -> None:
        """The exact Hierholzer circuit for A→B→C→A matches expected order."""
        graph = Graph(input_graph=json.dumps(circuit_json))
        circuit = find_circuit(graph)
        expected = ["A", "C", "B", "A"]
        assert circuit == expected
