import json
import shutil
import tempfile
import unittest
from os import path

import numpy as np

from graphworks.graph import Graph
from graphworks.graph import Edge


class GraphTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_name(self):
        graph = Graph("graph")
        self.assertEqual('graph', graph.get_label())

    def test_repr(self):
        graph = Graph("graph")
        self.assertEqual('graph', repr(graph))

    def test_str(self):
        answer = """my graph
A -> B
B -> 0"""
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertEqual(answer, str(graph))

    def test_edges(self):
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertEqual(json_graph['label'], graph.get_label())
        self.assertEqual(False, graph.is_directed())
        self.assertEqual(json_graph['graph'], graph.get_graph())
        self.assertEqual([Edge('A', 'B')], graph.edges())

    def test_add_vertex(self):
        graph = Graph("my graph")
        graph.add_vertex("A")
        self.assertEqual(['A'], graph.vertices())

    def test_add_edge(self):
        graph = Graph("my graph")
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        self.assertEqual(1, len(graph.edges()))
        graph.add_edge("X", "Y")
        self.assertEqual(2, len(graph.edges()))
        self.assertEqual(4, len(graph.vertices()))

    def test_read_graph_from_file(self):
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        with open(path.join(self.test_dir, 'test.txt'), 'w') as out_file:
            out_file.write(json.dumps(json_graph))
        graph = Graph(input_file=str(path.join(self.test_dir, 'test.txt')))
        self.assertEqual(json_graph["label"], graph.get_label())
        self.assertEqual(False, graph.is_directed())
        self.assertEqual(json_graph["graph"], graph.get_graph())

    def test_order_and_size(self):
        json_graph = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertEqual(2, graph.order())
        self.assertEqual(1, graph.size())

    def test_get_adjacency_matrix(self):
        json_graph = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        matrix = graph.get_adjacency_matrix()
        answer = np.array([[0, 1], [0, 0]])
        np.testing.assert_equal(matrix, answer)
        self.assertEqual(answer.size, matrix.size)

    def test_set_from_adjacency_matrix(self):
        array_graph = np.array([[0, 1], [1, 0]], dtype=object)
        graph = Graph(input_array=array_graph)
        self.assertEqual(2, len(graph.vertices()))
        self.assertEqual(1, len(graph.edges()))

    def test_malformed_array(self):
        array_graph = np.array([[0, 1, 0, 0, 0], [1, 0]], dtype=object)
        self.assertRaises(ValueError, Graph, input_array=array_graph)
        array_graph = np.array([[0, 1], [1, 0], [1, 0]])
        self.assertRaises(ValueError, Graph, input_array=array_graph)

    def test_malformed_json(self):
        json_graph = {"graph": {"A": ["B", "C", "D"], "B": []}}
        self.assertRaises(ValueError, Graph, input_graph=json.dumps(json_graph))

    def test_get_neighbors(self):
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))

        self.assertEqual(graph.get_neighbors("A"), ["B"])
        self.assertEqual(graph.get_neighbors("B"), [])


if __name__ == '__main__':
    unittest.main()
