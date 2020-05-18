import json
import unittest

from graphworks.algorithms.basic import find_isolated_nodes
from graphworks.algorithms.basic import generate_edges
from graphworks.graph import Graph


class BasicTests(unittest.TestCase):

    def test_generate_edges(self):
        json_graph = {"name": "", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        edges = generate_edges(graph)
        self.assertEqual(len(edges), 1)

    def test_find_isolated_nodes(self):
        json_graph = {"name": "", "graph": {"A": ["B"], "B": ["A"], "C": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        isolated = find_isolated_nodes(graph)
        self.assertEqual(len(isolated), 1)
        self.assertEqual(isolated[0], 'C')


if __name__ == '__main__':
    unittest.main()
