import json
import unittest
from graphworks.algorithms.directed import is_dag, find_circuit
from graphworks.graph import Graph


class DirectedTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_is_dag(self):
        cycle_graph = {
            "directed": True,
            "graph": {
                "A": ["B"],
                "B": ["C", "D"],
                "C": [],
                "D": ["E", "A"],  # cycle A -> B -> D -> A
                "E": []
            }
        }
        graph = Graph(input_graph=json.dumps(cycle_graph))
        self.assertFalse(is_dag(graph))
        dag = cycle_graph
        # remove the cycle
        dag["graph"]["D"] = ["E"]
        graph2 = Graph(input_graph=json.dumps(dag))
        self.assertTrue(is_dag(graph2))

    def test_find_circuit(self):
        circuit_graph = {
            "directed": True,
            "graph": {
                "A": ["B"],
                "B": ["C"],
                "C": ["A"]  # circuit A -> C -> B -> A
            }
        }
        graph = Graph(input_graph=json.dumps(circuit_graph))
        circuit = find_circuit(graph)
        expected_circuit = ["A", "C", "B", "A"]
        self.assertListEqual(circuit, expected_circuit)


if __name__ == '__main__':
    unittest.main()
