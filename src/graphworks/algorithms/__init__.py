"""Graph algorithm implementations.

Submodules
----------

- :mod:`~graphworks.algorithms.properties` — structural predicates, metrics, and the complement
- :mod:`~graphworks.algorithms.paths` — path finding and isolated vertices
- :mod:`~graphworks.algorithms.search` — graph traversal
- :mod:`~graphworks.algorithms.directed` — directed-graph algorithms
- :mod:`~graphworks.algorithms.sort` — sorting algorithms
"""

from .directed import find_circuit, is_dag
from .paths import find_all_paths, find_isolated_vertices, find_path
from .properties import (
    complement,
    degree_sequence,
    density,
    diameter,
    is_complete,
    is_connected,
    is_degree_sequence,
    is_dense,
    is_erdos_gallai,
    is_regular,
    is_simple,
    is_sparse,
    max_degree,
    min_degree,
    vertex_degree,
)
from .search import breadth_first_search, depth_first_search
from .sort import topological_sort

__all__ = [
    "breadth_first_search",
    "complement",
    "degree_sequence",
    "density",
    "depth_first_search",
    "diameter",
    "find_all_paths",
    "find_circuit",
    "find_isolated_vertices",
    "find_path",
    "is_complete",
    "is_connected",
    "is_dag",
    "is_degree_sequence",
    "is_dense",
    "is_erdos_gallai",
    "is_regular",
    "is_simple",
    "is_sparse",
    "max_degree",
    "min_degree",
    "topological_sort",
    "vertex_degree",
]
