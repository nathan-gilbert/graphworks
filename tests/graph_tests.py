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
        self.assertEqual(graph.name, 'graph')

    def test_repr(self):
        graph = Graph("graph")
        self.assertEqual(repr(graph), 'graph')

    def test_edges(self):
        json_graph = {"name": "my graph", "edges": {"A": "B", "B": None}}
        graph = Graph("graph", input_str=json.dumps(json_graph))
        self.assertEqual(graph.edges, json_graph["edges"])

    def test_read_graph_from_file(self):
        json_graph = {"name": "my graph", "edges": {"A": "B", "B": None}}
        with open(path.join(self.test_dir, 'test.txt'), 'w') as outFile:
            outFile.write(json.dumps(json_graph))
        graph = Graph("graph", input_file=str(path.join(self.test_dir, 'test.txt')))
        self.assertEqual(graph.edges, json_graph["edges"])


if __name__ == '__main__':
    unittest.main()
