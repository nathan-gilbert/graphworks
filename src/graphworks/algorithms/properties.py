"""
graphworks.algorithms.properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graph property queries and structural metrics.

This module provides predicate functions (``is_*``) and quantitative metrics
(``density``, ``diameter``, ``degree_sequence``, etc.) that inspect a
:class:`~graphworks.graph.Graph` without modifying it.

All functions are pure: they take a graph (and optional parameters) and
return a value.  None of the functions here require numpy.

:author: Nathan Gilbert
"""

from __future__ import annotations

from graphworks.graph import Graph
from graphworks.types import AdjacencyMatrix

# ---------------------------------------------------------------------------
# Degree helpers
# ---------------------------------------------------------------------------


def vertex_degree(graph: Graph, vertex: str) -> int:
    """Return the degree of *vertex*.

    Self-loops are counted twice (each loop contributes 2 to the degree).

    :param graph: The graph to inspect.
    :type graph: Graph
    :param vertex: Vertex name.
    :type vertex: str
    :return: Degree of *vertex*.
    :rtype: int
    """
    adj = graph[vertex]
    degree = len(adj)
    # each self-loop adds an extra 1
    degree += sum(1 for v in adj if v == vertex)
    return degree


def degree_sequence(graph: Graph) -> tuple[int, ...]:
    """Return the degree sequence of the graph in non-increasing order.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Sorted tuple of vertex degrees (highest first).
    :rtype: tuple[int, ...]
    """
    return tuple(
        sorted(
            (vertex_degree(graph, v) for v in graph.vertices()),
            reverse=True,
        )
    )


def min_degree(graph: Graph) -> int:
    """Return the minimum vertex degree in the graph.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Minimum degree across all vertices.
    :rtype: int
    """
    return min(vertex_degree(graph, v) for v in graph.vertices())


def max_degree(graph: Graph) -> int:
    """Return the maximum vertex degree in the graph.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Maximum degree across all vertices.
    :rtype: int
    """
    return max(vertex_degree(graph, v) for v in graph.vertices())


# ---------------------------------------------------------------------------
# Sequence predicates
# ---------------------------------------------------------------------------


def is_degree_sequence(sequence: list[int]) -> bool:
    """Return whether *sequence* is a valid degree sequence.

    A valid degree sequence has a non-negative, even sum and is
    non-increasing.

    :param sequence: Candidate degree sequence.
    :type sequence: list[int]
    :return: ``True`` if *sequence* is a valid degree sequence.
    :rtype: bool
    """
    if not sequence:
        return True
    return sum(sequence) % 2 == 0 and sequence == sorted(sequence, reverse=True)


def is_erdos_gallai(sequence: list[int]) -> bool:
    """Return whether *sequence* satisfies the Erdős–Gallai theorem.

    A non-increasing sequence of non-negative integers is a valid degree
    sequence of a simple graph if and only if its sum is even and the
    Erdős–Gallai condition holds for every prefix.

    :param sequence: Candidate degree sequence (need not be sorted).
    :type sequence: list[int]
    :return: ``True`` if *sequence* is graphical per Erdős–Gallai.
    :rtype: bool
    """
    if not sequence:
        return True

    seq = sorted(sequence, reverse=True)
    n = len(seq)

    if sum(seq) % 2 != 0:
        return False

    for k in range(1, n + 1):
        lhs = sum(seq[:k])
        rhs = k * (k - 1) + sum(min(d, k) for d in seq[k:])
        if lhs > rhs:
            return False
    return True


# ---------------------------------------------------------------------------
# Structural predicates
# ---------------------------------------------------------------------------


def is_regular(graph: Graph) -> bool:
    """Return whether every vertex in the graph has the same degree.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is regular (all degrees equal).
    :rtype: bool
    """
    degrees = [vertex_degree(graph, v) for v in graph.vertices()]
    return len(set(degrees)) <= 1


def is_simple(graph: Graph) -> bool:
    """Return whether the graph contains no self-loops.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if no vertex has an edge to itself.
    :rtype: bool
    """
    return all(v not in graph[v] for v in graph.vertices())


def is_connected(
    graph: Graph,
    start_vertex: str | None = None,
    vertices_encountered: set[str] | None = None,
) -> bool:
    """Return whether the graph is connected.

    Uses a recursive depth-first traversal from *start_vertex*.

    :param graph: The graph to inspect.
    :type graph: Graph
    :param start_vertex: Vertex to begin the traversal from.  Defaults to
        the first vertex in :meth:`~graphworks.graph.Graph.vertices`.
    :type start_vertex: str | None
    :param vertices_encountered: Set of already-visited vertices used by the
        recursive calls.  Callers should leave this as ``None``.
    :type vertices_encountered: set[str] | None
    :return: ``True`` if all vertices are reachable from *start_vertex*.
    :rtype: bool
    """
    if vertices_encountered is None:
        vertices_encountered = set()

    verts = graph.vertices()
    if not start_vertex:
        start_vertex = verts[0]

    vertices_encountered.add(start_vertex)

    if len(vertices_encountered) != len(verts):
        for vertex in graph[start_vertex]:
            if vertex not in vertices_encountered:
                if is_connected(graph, vertex, vertices_encountered):
                    return True
    else:
        return True
    return False


def is_complete(graph: Graph) -> bool:
    """Return whether the graph is complete.

    A complete graph has every possible edge.  Checks that the edge count
    equals ``V*(V-1)`` for directed graphs or ``V*(V-1)/2`` for undirected.

    Runtime: O(n²).

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is complete.
    :rtype: bool
    """
    v_count = len(graph.vertices())
    max_edges = v_count**2 - v_count
    if not graph.is_directed():
        max_edges //= 2

    if len(graph.edges()) != max_edges:
        return False

    return all(len(graph[v]) == v_count - 1 for v in graph)


def is_sparse(graph: Graph) -> bool:
    """Return whether the graph is sparse (``|E| ≤ |V|² / 2``).

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is sparse.
    :rtype: bool
    """
    return graph.size() <= (graph.order() ** 2 / 2)


def is_dense(graph: Graph) -> bool:
    """Return whether the graph is dense (``|E| = Θ(|V|²)``).

    Computed as density ≥ 0.5.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is dense.
    :rtype: bool
    """
    return density(graph) >= 0.5


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def density(graph: Graph) -> float:
    """Return the density of the graph.

    Density is ``2|E| / (|V|² - |V|)``.  Returns ``0.0`` for graphs with
    fewer than two vertices.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Density in the range ``[0.0, 1.0]``.
    :rtype: float
    """
    v_count = len(graph.vertices())
    if v_count < 2:
        return 0.0
    e_count = len(graph.edges())
    return 2.0 * (e_count / (v_count**2 - v_count))


def diameter(graph: Graph) -> int:
    """Return the diameter of the graph.

    The diameter is the length of the longest shortest path between any pair
    of vertices.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Diameter (number of edges on the longest shortest path).
    :rtype: int
    """
    from graphworks.algorithms.paths import find_all_paths  # avoid circular

    verts = graph.vertices()
    pairs = [
        (verts[i], verts[j])
        for i in range(len(verts) - 1)
        for j in range(i + 1, len(verts))
    ]

    shortest_paths: list[list[str]] = []
    for start, end in pairs:
        all_paths = find_all_paths(graph, start, end)
        if all_paths:
            shortest_paths.append(sorted(all_paths, key=len)[0])

    if not shortest_paths:
        return 0

    return len(max(shortest_paths, key=len)) - 1


# ---------------------------------------------------------------------------
# Matrix-based operations (stdlib only)
# ---------------------------------------------------------------------------


def invert(matrix: AdjacencyMatrix) -> AdjacencyMatrix:
    """Return the complement of an adjacency matrix.

    Flips ``0`` ↔ ``1`` for every cell, including the diagonal.

    :param matrix: Square adjacency matrix.
    :type matrix: AdjacencyMatrix
    :return: Inverted (complement) adjacency matrix.
    :rtype: AdjacencyMatrix
    """
    return [[1 - cell for cell in row] for row in matrix]


def get_complement(graph: Graph) -> Graph:
    """Return the complement graph of *graph*.

    The complement is the graph on the same vertex set whose edges are
    exactly the edges *not* present in *graph*.

    :param graph: The source graph.
    :type graph: Graph
    :return: Complement graph.
    :rtype: Graph
    """
    adj = graph.get_adjacency_matrix()
    complement_matrix = invert(adj)
    return Graph(
        label=f"{graph.get_label()} complement",
        input_matrix=complement_matrix,
    )
