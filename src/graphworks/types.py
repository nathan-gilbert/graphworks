"""
graphworks.types
~~~~~~~~~~~~~~~~

Shared type aliases used throughout the graphworks library.

These are intentionally stdlib-only. numpy interop lives in
:mod:`graphworks.numpy_compat` and is gated behind the ``[matrix]`` extra.

:author: Nathan Gilbert
"""

from __future__ import annotations

# A square 2-D adjacency matrix represented with pure Python lists.
# ``AdjacencyMatrix[i][j] == 1`` means an edge exists from vertex *i* to
# vertex *j*; ``0`` means no edge.
#
# Example (2-vertex graph with one directed edge 0 → 1)::
#
#     [[0, 1],
#      [0, 0]]
AdjacencyMatrix = list[list[int]]
