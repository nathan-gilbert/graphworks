import unittest

from graphworks.graph import Edge


class EdgeTests(unittest.TestCase):

    def test_has_weight(self):
        e = Edge('a', 'b', False)
        self.assertFalse(e.has_weight())
        f = Edge('a', 'b', True, 50.0)
        self.assertTrue(f.has_weight())
