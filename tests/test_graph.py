"""
tests.test_graph
~~~~~~~~~~~~~~~~

Unit tests for :class:`graphworks.graph.Graph`.

The numpy-dependent tests are skipped automatically when the ``[matrix]``
extra is not installed.
"""

import json
import shutil
import tempfile
import unittest
from os import path

from src.graphworks.edge import Edge
from src.graphworks.graph import Graph

try:
    import numpy as np

    from src.graphworks.numpy_compat import matrix_to_ndarray, ndarray_to_matrix

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class GraphLabelTests(unittest.TestCase):
    """Tests for graph label and repr behaviour."""

    def test_name(self):
        graph = Graph("graph")
        self.assertEqual("graph", graph.get_label())

    def test_repr(self):
        graph = Graph("graph")
        self.assertEqual("graph", repr(graph))

    def test_str(self):
        answer = "my graph\nA -> B\nB -> 0"
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertEqual(answer, str(graph))


class GraphEdgeVertexTests(unittest.TestCase):
    """Tests for vertex and edge manipulation."""

    def test_edges(self):
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertEqual(json_graph["label"], graph.get_label())
        self.assertFalse(graph.is_directed())
        self.assertEqual(json_graph["graph"], graph.get_graph())
        self.assertEqual([Edge("A", "B")], graph.edges())

    def test_add_vertex(self):
        graph = Graph("my graph")
        graph.add_vertex("A")
        self.assertEqual(["A"], graph.vertices())

    def test_add_edge(self):
        graph = Graph("my graph")
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        self.assertEqual(1, len(graph.edges()))
        graph.add_edge("X", "Y")
        self.assertEqual(2, len(graph.edges()))
        self.assertEqual(4, len(graph.vertices()))

    def test_order_and_size(self):
        json_graph = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertEqual(2, graph.order())
        self.assertEqual(1, graph.size())

    def test_get_neighbors(self):
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        self.assertEqual(["B"], graph.get_neighbors("A"))
        self.assertEqual([], graph.get_neighbors("B"))


class GraphFileTests(unittest.TestCase):
    """Tests for file-based graph construction."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_graph_from_file(self):
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        file_path = path.join(self.test_dir, "test.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_graph))

        graph = Graph(input_file=file_path)
        self.assertEqual(json_graph["label"], graph.get_label())
        self.assertFalse(graph.is_directed())
        self.assertEqual(json_graph["graph"], graph.get_graph())


class GraphAdjacencyMatrixTests(unittest.TestCase):
    """Tests for the stdlib adjacency matrix interface."""

    def test_get_adjacency_matrix(self):
        json_graph = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        matrix = graph.get_adjacency_matrix()
        # A -> B means matrix[0][1] = 1; all others 0
        self.assertEqual([[0, 1], [0, 0]], matrix)

    def test_set_from_adjacency_matrix(self):
        matrix: list[list[int]] = [[0, 1], [1, 0]]
        graph = Graph(input_matrix=matrix)
        self.assertEqual(2, len(graph.vertices()))
        self.assertEqual(1, len(graph.edges()))

    def test_malformed_matrix_non_square(self):
        with self.assertRaises(ValueError):
            Graph(input_matrix=[[0, 1, 0], [1, 0]])

    def test_malformed_matrix_wrong_row_count(self):
        with self.assertRaises(ValueError):
            Graph(input_matrix=[[0, 1], [1, 0], [1, 0]])

    def test_matrix_index_helpers(self):
        json_graph = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        idx = graph.vertex_to_matrix_index("A")
        self.assertEqual("A", graph.matrix_index_to_vertex(idx))


class GraphValidationTests(unittest.TestCase):
    """Tests for graph construction validation."""

    def test_malformed_json_missing_vertex(self):
        json_graph = {"graph": {"A": ["B", "C", "D"], "B": []}}
        with self.assertRaises(ValueError):
            Graph(input_graph=json.dumps(json_graph))


@unittest.skipUnless(HAS_NUMPY, "numpy not installed — skipping numpy interop tests")
class GraphNumpyCompatTests(unittest.TestCase):
    """Tests for numpy ndarray interop via graphworks.numpy_compat.

    These tests are skipped automatically when numpy is not installed.
    Install with: ``pip install graphworks[matrix]``
    """

    def test_ndarray_to_matrix(self):
        arr = np.array([[0, 1], [1, 0]])
        matrix = ndarray_to_matrix(arr)
        self.assertEqual([[0, 1], [1, 0]], matrix)

    def test_matrix_to_ndarray(self):
        matrix = [[0, 1], [1, 0]]
        arr = matrix_to_ndarray(matrix)
        np.testing.assert_array_equal(arr, np.array([[0, 1], [1, 0]]))

    def test_graph_from_ndarray_via_compat(self):
        arr = np.array([[0, 1], [1, 0]], dtype=object)
        matrix = ndarray_to_matrix(arr)
        graph = Graph(input_matrix=matrix)
        self.assertEqual(2, len(graph.vertices()))
        self.assertEqual(1, len(graph.edges()))

    def test_malformed_ndarray_non_square(self):
        arr = np.array([[0, 1, 0, 0, 0], [1, 0]], dtype=object)
        with self.assertRaises(ValueError):
            ndarray_to_matrix(arr)

    def test_adjacency_matrix_roundtrip(self):
        json_graph = {"graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        stdlib_matrix = graph.get_adjacency_matrix()
        np_arr = matrix_to_ndarray(stdlib_matrix)
        np.testing.assert_array_equal(np_arr, np.array([[0, 1], [0, 0]]))


if __name__ == "__main__":
    unittest.main()
