import json
import unittest

from graphworks.algorithms.search import breadth_first_search
from graphworks.algorithms.search import depth_first_search
from graphworks.graph import Graph


class SearchTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simple_graph = {"graph": {
            "a": ["b", "c"],
            "b": ["c"],
            "c": ["a", "d"],
            "d": ["d"]
        }}

    def test_breadth_first_search(self):
        graph = Graph(input_graph=json.dumps(self.simple_graph))
        walk = breadth_first_search(graph, "c")
        self.assertListEqual(["c", "a", "d", "b"], walk)

    def test_depth_first_search(self):
        graph = Graph(input_graph=json.dumps(self.simple_graph))
        walk = depth_first_search(graph, "c")
        self.assertListEqual(["c", "d", "a", "b"], walk)


if __name__ == '__main__':
    unittest.main()
