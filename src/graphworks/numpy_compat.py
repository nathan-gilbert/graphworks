"""Optional numpy interop for graphworks.

This module is **only available** when the ``[matrix]`` extra is installed::

    pip install graphworks[matrix]

It provides thin conversion helpers between :data:`~graphworks.types.AdjacencyMatrix`
(``list[list[int]]``) and ``numpy.ndarray`` so callers who already have numpy
arrays can pass them directly to :class:`~graphworks.graph.Graph`.

Import pattern — always guard with :data:`TYPE_CHECKING` or a try/except so that
code using graphworks does not *require* numpy::

    >>> try:
    ...    from graphworks.numpy_compat import ndarray_to_matrix, matrix_to_ndarray
    >>> except ImportError:
    ...    pass  # numpy not installed; matrix I/O unavailable

:author: Nathan Gilbert
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from graphworks.types import AdjacencyMatrix

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "numpy is required for numpy interop. " "Install it with: pip install graphworks[matrix]"
    ) from exc


def ndarray_to_matrix(arr: NDArray) -> AdjacencyMatrix:
    """Convert numpy ndarray adjacency representation to :data:`~graphworks.types.AdjacencyMatrix`.

    Only integer-valued arrays are supported. Values greater than zero are treated as edges (
    coerced to ``1``); zero values mean no edge.

    :param arr: A square 2-D numpy array representing an adjacency matrix.
    :type arr: numpy.typing.NDArray
    :raises ValueError: If *arr* is not a 2-D square array.
    :return: A pure-Python adjacency matrix.
    :rtype: AdjacencyMatrix
    """
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError(f"Expected a square 2-D array, got shape {arr.shape}")
    return [[1 if int(val) > 0 else 0 for val in row] for row in arr]


def matrix_to_ndarray(matrix: AdjacencyMatrix) -> NDArray:
    """Convert an :data:`~graphworks.types.AdjacencyMatrix` to a numpy ndarray.

    :param matrix: A square pure-Python adjacency matrix.
    :type matrix: AdjacencyMatrix
    :return: A 2-D numpy integer array with dtype ``numpy.int_``.
    :rtype: numpy.typing.NDArray
    """
    return np.array(matrix, dtype=np.int_)
