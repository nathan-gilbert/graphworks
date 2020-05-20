import json
import unittest

from graphworks.algorithms.basic import density
from graphworks.algorithms.basic import find_all_paths
from graphworks.algorithms.basic import find_isolated_vertices
from graphworks.algorithms.basic import find_path
from graphworks.algorithms.basic import generate_edges
from graphworks.algorithms.basic import vertex_degree
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
        isolated = find_isolated_vertices(graph)
        self.assertEqual(len(isolated), 1)
        self.assertEqual(isolated[0], 'C')

    def test_find_path(self):
        json_graph = {"label": "test",
                      "directed": False,
                      "graph":
                          {"a": ["d"],
                           "b": ["c"],
                           "c": ["b", "c", "d", "e"],
                           "d": ["a", "c"],
                           "e": ["c"],
                           "f": []}
                      }
        graph = Graph(input_graph=json.dumps(json_graph))
        path = find_path(graph, "a", "b")
        self.assertListEqual(['a', 'd', 'c', 'b'], path)
        path = find_path(graph, "a", "f")
        self.assertListEqual([], path)
        path = find_path(graph, "c", "c")
        self.assertListEqual(['c'], path)
        path = find_path(graph, "z", "a")
        self.assertListEqual([], path)

    def test_find_all_paths(self):
        json_graph = {"label": "test2",
                      "directed": False,
                      "graph":
                          {"a": ["d", "f"],
                           "b": ["c"],
                           "c": ["b", "c", "d", "e"],
                           "d": ["a", "c"],
                           "e": ["c"],
                           "f": ["d"]}
                      }
        graph = Graph(input_graph=json.dumps(json_graph))
        paths = find_all_paths(graph, "a", "b")
        self.assertListEqual([['a', 'd', 'c', 'b'], ['a', 'f', 'd', 'c', 'b']], paths)
        paths = find_all_paths(graph, "z", "b")
        self.assertListEqual([], paths)

    def test_vertex_degree(self):
        json_graph = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(json_graph))
        deg = vertex_degree(graph, 'a')
        self.assertEqual(4, deg)

    def test_density(self):
        dense_graph = {"graph": {"a": ["d", "f"],
                                 "b": ["c", "b"],
                                 "c": ["b", "c", "d", "e"],
                                 "d": ["a", "c"],
                                 "e": ["c"],
                                 "f": ["a"]
                                 }}
        graph = Graph(input_graph=json.dumps(dense_graph))
        self.assertAlmostEqual(0.466666666667, density(graph))

        complete_graph = {"graph": {
            "a": ["b", "c"],
            "b": ["a", "c"],
            "c": ["a", "b"]
        }}
        graph = Graph(input_graph=json.dumps(complete_graph))
        self.assertEqual(1.0, density(graph))

        isolated_graph = {"graph": {
            "a": [],
            "b": [],
            "c": []
        }}
        graph = Graph(input_graph=json.dumps(isolated_graph))
        self.assertEqual(0.0, density(graph))


if __name__ == '__main__':
    unittest.main()
