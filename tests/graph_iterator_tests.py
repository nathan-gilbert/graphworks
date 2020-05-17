import json
import unittest
from graphworks.graph import Graph


class GraphIteratorTests(unittest.TestCase):
    def test_iterator(self):
        json_graph = {"name": "my graph",
                      "edges": {"A": ["B", "C", "D"],
                                "B": [],
                                "C": [],
                                "D": []}
                      }
        graph = Graph(input_graph=json.dumps(json_graph))

        iterations = 0
        for _ in graph:
            iterations += 1
        self.assertEqual(iterations, 4)


if __name__ == '__main__':
    unittest.main()
