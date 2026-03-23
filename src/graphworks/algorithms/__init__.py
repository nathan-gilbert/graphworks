"""Graph algorithm implementations.

Submodules
----------

- :mod:`~graphworks.algorithms.properties` — structural predicates and metrics
  (``is_connected``, ``density``, ``diameter``, ``degree_sequence``, etc.)
- :mod:`~graphworks.algorithms.paths` — path finding and edge utilities
  (``find_path``, ``find_all_paths``, ``generate_edges``, etc.)
- :mod:`~graphworks.algorithms.search` — graph traversal
  (``breadth_first_search``, ``depth_first_search``, etc.)
- :mod:`~graphworks.algorithms.directed` — directed-graph algorithms
  (``is_dag``, ``find_circuit``, etc.)
- :mod:`~graphworks.algorithms.sort` — sorting algorithms
  (``topological``, etc.)
"""

from graphworks.algorithms.directed import find_circuit, is_dag
from graphworks.algorithms.paths import (
    find_all_paths,
    find_isolated_vertices,
    find_path,
    generate_edges,
)
from graphworks.algorithms.properties import (
    degree_sequence,
    density,
    diameter,
    get_complement,
    invert,
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
from graphworks.algorithms.search import (
    arrival_departure_dfs,
    breadth_first_search,
    depth_first_search,
)
from graphworks.algorithms.sort import topological

__all__ = [
    # properties
    "degree_sequence",
    "density",
    "diameter",
    "get_complement",
    "invert",
    "is_complete",
    "is_connected",
    "is_dense",
    "is_degree_sequence",
    "is_erdos_gallai",
    "is_regular",
    "is_simple",
    "is_sparse",
    "max_degree",
    "min_degree",
    "vertex_degree",
    # paths
    "find_all_paths",
    "find_isolated_vertices",
    "find_path",
    "generate_edges",
    # search
    "arrival_departure_dfs",
    "breadth_first_search",
    "depth_first_search",
    # directed
    "find_circuit",
    "is_dag",
    # sort
    "topological",
]
