import unittest
import json
from graphworks.graph import Graph
from graphworks.algorithms.basic import generate_edges, find_isolated_nodes


class BasicTests(unittest.TestCase):

    def test_generate_edges(self):
        json_graph = {"name": "", "edges": {"A": ["B"], "B": []}}
        g = Graph(input_graph=json.dumps(json_graph))
        edges = generate_edges(g)
        self.assertEqual(len(edges), 1)

    def test_find_isolated_nodes(self):
        json_graph = {"name": "", "edges": {"A": ["B"], "B": ["A"], "C": []}}
        g = Graph(input_graph=json.dumps(json_graph))
        isolated = find_isolated_nodes(g)
        self.assertEqual(len(isolated), 1)
        self.assertEqual(isolated[0], 'C')


if __name__ == '__main__':
    unittest.main()

