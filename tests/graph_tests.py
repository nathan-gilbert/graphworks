import shutil
import tempfile
import unittest
import json
from os import path

from graphworks.graph import Graph


class GraphTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_name(self):
        graph = Graph("graph")
        self.assertEqual(graph.get_label(), 'graph')

    def test_repr(self):
        graph = Graph("graph")
        self.assertEqual(repr(graph), 'graph')

    def test_str(self):
        answer = """my graph
A -> B
B -> 0"""
        json_graph = {"name": "my graph", "edges": {"A": "B", "B": None}}
        graph = Graph(input_str=json.dumps(json_graph))
        self.assertEqual(str(graph), answer)

    def test_edges(self):
        json_graph = {"name": "my graph", "edges": {"A": "B", "B": None}}
        graph = Graph(input_str=json.dumps(json_graph))
        self.assertEqual(graph.get_label(), json_graph["name"])
        self.assertEqual(graph.edges, json_graph["edges"])

    def test_read_graph_from_file(self):
        json_graph = {"name": "my graph", "edges": {"A": "B", "B": None}}
        with open(path.join(self.test_dir, 'test.txt'), 'w') as outFile:
            outFile.write(json.dumps(json_graph))
        graph = Graph(input_file=str(path.join(self.test_dir, 'test.txt')))
        self.assertEqual(graph.get_label(), json_graph["name"])
        self.assertEqual(graph.edges, json_graph["edges"])


if __name__ == '__main__':
    unittest.main()
