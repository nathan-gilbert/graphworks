import json
import unittest

from graphworks.algorithms.basic import degree_sequence
from graphworks.algorithms.basic import density
from graphworks.algorithms.basic import diameter
from graphworks.algorithms.basic import find_all_paths
from graphworks.algorithms.basic import find_isolated_vertices
from graphworks.algorithms.basic import find_path
from graphworks.algorithms.basic import generate_edges
from graphworks.algorithms.basic import is_connected
from graphworks.algorithms.basic import is_degree_sequence
from graphworks.algorithms.basic import is_erdos_gallai
from graphworks.algorithms.basic import is_regular
from graphworks.algorithms.basic import is_simple
from graphworks.algorithms.basic import is_sparse
from graphworks.algorithms.basic import max_degree
from graphworks.algorithms.basic import min_degree
from graphworks.algorithms.basic import vertex_degree
from graphworks.algorithms.basic import get_complement
from graphworks.algorithms.basic import is_complete
from graphworks.graph import Graph


class BasicTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected_graph = {
            "graph": {"a": ["d", "f"],
                      "b": ["c", "b"],
                      "c": ["b", "c", "d", "e"],
                      "d": ["a", "c"],
                      "e": ["c"],
                      "f": ["a"]}
        }
        self.complete_graph = {
            "graph": {"a": ["b", "c"],
                      "b": ["a", "c"],
                      "c": ["a", "b"]}
        }
        self.complete_digraph = {
            "directed": True,
            "graph": {
                "a": ["b"],
                "b": ["a"]
            }
        }
        self.isolated_graph = {"graph": {"a": [], "b": [], "c": []}}
        self.big_graph = {"graph": {
            "a": ["c"],
            "b": ["c", "e", "f"],
            "c": ["a", "b", "d", "e"],
            "d": ["c"],
            "e": ["b", "c", "f"],
            "f": ["b", "e"]
        }}
        self.one_regular_graph = {"graph": {
            "a": [],
            "b": [],
            "c": []
        }}
        self.lollipop_graph = {"graph": {
            "z": ["a"],
            "a": ["b"],
            "b": ["c"],
            "c": ["d"],
            "d": ["b"]
        }}
        self.straight_line = {"graph": {
            "a": ["b"],
            "b": ["c"],
            "c": ["d"],
            "d": []
        }}

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

    def test_graph_min_degree(self):
        json_graph = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(json_graph))
        min_deg = min_degree(graph)
        self.assertEqual(1, min_deg)

    def test_graph_max_degree(self):
        json_graph = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(json_graph))
        max_deg = max_degree(graph)
        self.assertEqual(4, max_deg)

    def test_degree_sequence(self):
        json_graph = {"graph": {"a": ["a", "b", "c"], "b": ["a"], "c": ["a"]}}
        graph = Graph(input_graph=json.dumps(json_graph))
        dseq = degree_sequence(graph)
        self.assertEqual((4, 1, 1), dseq)

    def test_is_degree_sequence(self):
        self.assertEqual(False, is_degree_sequence([1, 2, 3]))
        self.assertEqual(True, is_degree_sequence([3, 1, 1]))
        self.assertEqual(True, is_degree_sequence([]))

    def test_is_erdos_gallois(self):
        self.assertEqual(True, is_erdos_gallai([]))
        self.assertEqual(False, is_erdos_gallai([1]))
        self.assertEqual(False, is_erdos_gallai([2, 2, 4]))
        self.assertEqual(False, is_erdos_gallai([32, 8, 4, 2, 2]))
        # a real graphic sequence
        self.assertEqual(True, is_erdos_gallai([6, 6, 6, 6, 5, 5, 2, 2]))

    def test_density(self):
        graph = Graph(input_graph=json.dumps(self.connected_graph))
        self.assertAlmostEqual(0.4666666666666667, density(graph))

        graph = Graph(input_graph=json.dumps(self.complete_graph))
        self.assertEqual(1.0, density(graph))

        graph = Graph(input_graph=json.dumps(self.isolated_graph))
        self.assertEqual(0.0, density(graph))

    def test_is_connected(self):
        graph = Graph(input_graph=json.dumps(self.connected_graph))
        self.assertTrue(is_connected(graph))

    def test_diameter(self):
        graph = Graph(input_graph=json.dumps(self.big_graph))
        self.assertEqual(3, diameter(graph))

    def test_is_regular_graph(self):
        graph = Graph(input_graph=json.dumps(self.big_graph))
        self.assertFalse(is_regular(graph))
        one_reg_graph = Graph(input_graph=json.dumps(self.one_regular_graph))
        self.assertTrue(is_regular(one_reg_graph))

    def test_is_simple(self):
        graph = Graph(input_graph=json.dumps(self.straight_line))
        self.assertTrue(is_simple(graph))
        lolli = Graph(input_graph=json.dumps(self.lollipop_graph))
        self.assertFalse(is_simple(lolli))

    def test_is_sparse(self):
        graph = Graph(input_graph=json.dumps(self.isolated_graph))
        self.assertTrue(is_sparse(graph))

    def test_is_complete(self):
        graph = Graph(input_graph=json.dumps(self.complete_graph))
        self.assertTrue(is_complete(graph))
        graph = Graph(input_graph=json.dumps(self.isolated_graph))
        self.assertFalse(is_complete(graph))
        json_graph = {"name": "", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertFalse(is_complete(graph))

    def test_complete_digraph(self):
        graph = Graph(input_graph=json.dumps(self.complete_digraph))
        self.assertTrue(is_complete(graph))
        json_graph = {"name": "", "directed": True, "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertFalse(is_complete(graph))

    def test_complement(self):
        graph = Graph(input_graph=json.dumps(self.isolated_graph))
        complement = get_complement(graph)
        self.assertTrue(is_complete(complement))


if __name__ == '__main__':
    unittest.main()
