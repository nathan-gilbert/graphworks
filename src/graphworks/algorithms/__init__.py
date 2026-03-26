"""Graph algorithm implementations.

Submodules
----------

- :mod:`~graphworks.algorithms.properties` — structural predicates and metrics
- :mod:`~graphworks.algorithms.paths` — path finding and edge utilities
- :mod:`~graphworks.algorithms.search` — graph traversal
- :mod:`~graphworks.algorithms.directed` — directed-graph algorithms
- :mod:`~graphworks.algorithms.sort` — sorting algorithms
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
    "arrival_departure_dfs",
    "breadth_first_search",
    "degree_sequence",
    "density",
    "depth_first_search",
    "diameter",
    "find_all_paths",
    "find_circuit",
    "find_isolated_vertices",
    "find_path",
    "generate_edges",
    "get_complement",
    "invert",
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
    "topological",
    "vertex_degree",
]
