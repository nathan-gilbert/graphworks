"""Graphworks — graph theoretic classes and algorithm helper functions.

A zero-dependency Python library for graph theory computation.  Provides a :class:`Graph` class
using adjacency-list storage, immutable :class:`Vertex` and :class:`Edge` value objects,
and pure-function algorithm modules for traversal, path-finding, properties, and directed graph
operations.

Quick start::

    >>> from graphworks import Graph
    >>> import json
    >>> data = {"label": "demo", "graph": {"A": ["B", "C"], "B": [], "C": []}}
    >>> g = Graph(input_graph=json.dumps(data))
    >>> g.order
    3
    >>> g.vertices()
    ['A', 'B', 'C']

Optional extras add numpy matrix interop (``[matrix]``) and Graphviz export (``[viz]``).
"""

from __future__ import annotations

from ._version import __version__, __version_tuple__
from .edge import Edge
from .graph import Graph
from .types import AdjacencyMatrix
from .vertex import Vertex

__all__ = ["AdjacencyMatrix", "Edge", "Graph", "Vertex", "__version__", "__version_tuple__"]

# ---- Package metadata (PEP 566 / importlib.metadata style) ----

__author__ = "Nathan Gilbert"
__author_email__ = "nathan.gilbert@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/nathan-gilbert/graphworks"
__description__ = "Graph theoretic classes and algorithm helper functions."
