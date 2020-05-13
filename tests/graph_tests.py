import unittest
import json

from graphworks.graph import Graph


class GraphTests(unittest.TestCase):
    def test_name(self):
        graph = Graph("graph")
        self.assertEqual(graph.name, 'graph')

    def test_edges(self):
        json_graph = {"name": "my graph", "edge": {"A": "B", "B": None}}
        graph = Graph("graph", json.dumps(json_graph))
        self.assertEqual(graph.edges, json_graph["edges"])


if __name__ == '__main__':
    unittest.main()
