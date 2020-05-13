import unittest

from graphworks.graph import Graph


class GraphTests(unittest.TestCase):
    def test_name(self):
        g = Graph("graph")
        self.assertEqual(g.name, 'graph')


if __name__ == '__main__':
    unittest.main()
