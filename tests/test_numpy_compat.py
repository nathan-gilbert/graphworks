"""Unit tests for :mod:`graphworks.numpy_compat`.

These tests are automatically skipped when numpy is not installed.
Install the optional dependency with::

    pip install graphworks[matrix]
"""

from __future__ import annotations

import pytest

numpy = pytest.importorskip("numpy", reason="numpy not installed — skipping matrix tests")
np = numpy

from graphworks.graph import Graph  # noqa: E402
from graphworks.numpy_compat import matrix_to_ndarray, ndarray_to_matrix  # noqa: E402


class TestNdarrayToMatrix:
    """Tests for ndarray_to_matrix."""

    def test_basic_conversion(self) -> None:
        arr = np.array([[0, 1], [1, 0]])
        assert ndarray_to_matrix(arr) == [[0, 1], [1, 0]]

    def test_nonzero_values_coerced_to_one(self) -> None:
        arr = np.array([[0, 5], [2, 0]])
        assert ndarray_to_matrix(arr) == [[0, 1], [1, 0]]

    def test_zero_values_remain_zero(self) -> None:
        arr = np.zeros((3, 3), dtype=int)
        assert ndarray_to_matrix(arr) == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def test_non_square_raises_value_error(self) -> None:
        arr = np.array([[0, 1, 0, 0, 0], [1, 0]], dtype=object)
        with pytest.raises(ValueError):  # noqa: PT011
            ndarray_to_matrix(arr)

    def test_three_dimensional_raises_value_error(self) -> None:
        arr = np.zeros((2, 2, 2))
        with pytest.raises(ValueError):  # noqa: PT011
            ndarray_to_matrix(arr)

    def test_result_is_list_of_lists(self) -> None:
        arr = np.eye(2, dtype=int)
        result = ndarray_to_matrix(arr)
        assert isinstance(result, list)
        assert all(isinstance(row, list) for row in result)


class TestMatrixToNdarray:
    """Tests for matrix_to_ndarray."""

    def test_basic_conversion(self) -> None:
        matrix = [[0, 1], [1, 0]]
        result = matrix_to_ndarray(matrix)
        np.testing.assert_array_equal(result, np.array([[0, 1], [1, 0]]))

    def test_dtype_is_integer(self) -> None:
        result = matrix_to_ndarray([[0, 1], [1, 0]])
        assert np.issubdtype(result.dtype, np.integer)

    def test_zeros_matrix(self) -> None:
        result = matrix_to_ndarray([[0, 0], [0, 0]])
        np.testing.assert_array_equal(result, np.zeros((2, 2), dtype=int))

    def test_result_is_ndarray(self) -> None:
        result = matrix_to_ndarray([[0, 1], [1, 0]])
        assert isinstance(result, np.ndarray)

    def test_shape_preserved(self) -> None:
        result = matrix_to_ndarray([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
        assert result.shape == (3, 3)


class TestGraphNumpyIntegration:
    """Integration tests for Graph ↔ numpy ndarray round-trips."""

    def test_graph_from_ndarray_via_compat(self) -> None:
        arr = np.array([[0, 1], [1, 0]], dtype=object)
        matrix = ndarray_to_matrix(arr)
        graph = Graph(input_matrix=matrix)
        assert graph.order == 2
        assert len(graph.edges()) == 1

    def test_symmetric_matrix_roundtrip(self) -> None:
        original = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        arr = matrix_to_ndarray(original)
        recovered = ndarray_to_matrix(arr)
        assert original == recovered

    def test_graph_order_from_ndarray(self) -> None:
        arr = np.zeros((4, 4), dtype=int)
        arr[0, 1] = 1
        arr[1, 0] = 1
        graph = Graph(input_matrix=ndarray_to_matrix(arr))
        assert graph.order == 4
