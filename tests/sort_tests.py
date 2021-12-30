import json
import unittest

from graphworks.algorithms.sort import topological
from graphworks.graph import Graph


class SortTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_topological_sort(self):
        t_sort_graph = {
            "directed": True,
            "graph": {
                "A": [],
                "B": [],
                "C": ["D"],
                "D": ["B"],
                "E": ["A", "B"],
                "F": ["A", "C"]
            }
        }
        graph = Graph(input_graph=json.dumps(t_sort_graph))

        expected_results = ["F", "E", "C", "D", "B", "A"]
        results = topological(graph)
        self.assertListEqual(expected_results, results)


if __name__ == '__main__':
    unittest.main()
